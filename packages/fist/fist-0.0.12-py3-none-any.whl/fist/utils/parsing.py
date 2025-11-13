import html
import re
import uuid
from collections import defaultdict
from functools import cache, cached_property
from operator import attrgetter
from typing import TypeVar, cast

from stix2 import (
    TLP_WHITE,
    AttackPattern,
    CourseOfAction,
    Identity,
    MarkingDefinition,
    MemoryStore,
    Note,
    Relationship,
    StatementMarking,
    Tool,
)
from stix2.base import SCO_DET_ID_NAMESPACE, _STIXBase
from stix2.canonicalization.Canonicalize import canonicalize

from ..models import Base, Bundle
from .common import VERSION
from .sdo import MitreDataComponent, MitreDataSource, MitreMatrix, MitreTactic

T = TypeVar("T", bound=_STIXBase, covariant=True)

_BLANK = "(空白)"
"""The default display string for blank fields."""


class Stix:

    def __init__(self, bundle: Bundle):
        self.bundle = bundle
        self.X_SOURCE_ID = f"x_{self.bundle.source.lower()}_id"
        self.DEFAULT_AUTHOR = Identity(
            id=self.generate_id(
                Identity,
                **{self.X_SOURCE_ID: "NICS"},
            ),
            name="National Institute of Cyber Security",
            identity_class="organization",
            confidence=100,
        )

    @staticmethod
    def generate_id(t: type[T], *, name: str | None = None, **kwargs):
        if name:
            kwargs.setdefault("name", name.lower().strip())
        return f"{t._type}--{uuid.uuid5(SCO_DET_ID_NAMESPACE, canonicalize(kwargs, utf8=False))}"

    @cached_property
    def marking_definitions(self):
        """Custom Marking references, including TLP and our Copyright."""
        return [
            # [TRAFFIC LIGHT PROTOCOL (TLP)](https://www.first.org/tlp)
            TLP_WHITE,
            # Copyright / License
            MarkingDefinition(
                id=self.generate_id(
                    MarkingDefinition,
                    definition=(
                        definition := StatementMarking(
                            statement="Copyright © 2024 NICS"
                        )
                    ).serialize(),
                    definition_type=(definition_type := "statement"),
                ),
                definition_type=definition_type,
                # Do not use `self._get_created_by_ref` which will cause an infinite loop.
                created_by_ref=self.DEFAULT_AUTHOR["id"],
                name="NICS",
                definition=definition,
            ),
        ]

    @cached_property
    def identities(self):
        """Individual and organizational contributors' identities."""
        return [
            Identity(
                id=self.generate_id(
                    Identity,
                    **{self.X_SOURCE_ID: contributor.id},
                ),
                name=contributor.name,
                description=contributor.description,
                external_references=contributor.model_dump(
                    mode="json", include=(_ := "external_references")
                )[_],
                identity_class=contributor.type,
                contact_information=contributor.contact,
                sectors=contributor.sectors,
                object_marking_refs=self.marking_definitions,
                # Do not use `self._get_created_by_ref` which will cause an infinite loop.
                created_by_ref=self.DEFAULT_AUTHOR["id"],
                confidence=100,
                custom_properties={
                    "x_opencti_aliases": [contributor.id],
                    "x_opencti_firstname": contributor.firstname,
                    "x_opencti_lastname": contributor.lastname,
                    "x_opencti_organization_type": contributor.organization_type,
                    "x_opencti_reliability": contributor.reliability,
                    self.X_SOURCE_ID: contributor.id,
                },
            )
            for contributor in self.bundle.contributors
        ]

    @cached_property
    def attack_patterns(self):
        return [
            AttackPattern(
                id=self.generate_id(
                    AttackPattern,
                    **{self.X_SOURCE_ID: technique.id},
                ),
                name=technique.name,
                description=technique.description,
                external_references=technique.model_dump(
                    mode="json", include=(_ := "external_references")
                )[_],
                aliases=[technique.id],
                object_marking_refs=self.marking_definitions,
                created_by_ref=self._get_created_by_ref(*technique.contributors),
                confidence=100,
                kill_chain_phases=[
                    {
                        "kill_chain_name": self.bundle.source,
                        "phase_name": (
                            tactic.name
                            if (tactic := self.bundle.get_tactic(technique.tactic_id))
                            else technique.tactic_id
                        ),
                    }
                ],
                custom_properties={
                    "x_mitre_contributors": list(
                        set(
                            self._get_contributor_name(contributor)
                            for contributor in technique.contributors
                        )
                    ),
                    "x_mitre_detection": technique.detection.description,
                    "x_mitre_id": technique.id,
                    "x_mitre_is_subtechnique": bool(technique.parent_id),
                    "x_mitre_permissions_required": technique.permissions,
                    "x_mitre_platforms": technique.platforms,
                    self.X_SOURCE_ID: technique.id,
                },
            )
            for technique in self.bundle.techniques
        ]

    @cached_property
    def course_of_actions(self):
        return [
            CourseOfAction(
                id=self.generate_id(
                    CourseOfAction,
                    **{self.X_SOURCE_ID: mitigation.id},
                ),
                name=mitigation.name,
                description=mitigation.description,
                external_references=mitigation.model_dump(
                    mode="json", include=(_ := "external_references")
                )[_],
                object_marking_refs=self.marking_definitions,
                confidence=100,
                created_by_ref=self._get_created_by_ref(*mitigation.contributors),
                custom_properties={
                    "x_mitre_contributors": list(
                        set(
                            self._get_contributor_name(contributor)
                            for contributor in mitigation.contributors
                        )
                    ),
                    self.X_SOURCE_ID: mitigation.id,
                },
            )
            for mitigation in self.bundle.mitigations
        ]

    @cached_property
    def tools(self):
        return [
            Tool(
                id=self.generate_id(
                    Tool,
                    **{self.X_SOURCE_ID: tool.id},
                ),
                name=tool.name,
                description=tool.description,
                external_references=tool.model_dump(
                    mode="json", include=(_ := "external_references")
                )[_],
                object_marking_refs=self.marking_definitions,
                confidence=100,
                created_by_ref=self._get_created_by_ref(*tool.contributors),
                tool_types=tool.tool_types,
                tool_version=tool.tool_version,
                kill_chain_phases=[
                    {
                        "kill_chain_name": self.bundle.source,
                        "phase_name": (
                            tactic.name
                            if (tactic := self.bundle.get_tactic(technique.tactic_id))
                            else technique.tactic_id
                        ),
                    }
                    for technique, _ in self.bundle.get_techniques(tool_id=tool.id)
                ],
                custom_properties={
                    "x_mitre_contributors": list(
                        set(
                            self._get_contributor_name(contributor)
                            for contributor in tool.contributors
                        )
                    ),
                    "x_mitre_platforms": tool.platforms,
                    self.X_SOURCE_ID: tool.id,
                },
            )
            for tool in self.bundle.tools
        ]

    @cached_property
    def notes(self):
        return [
            Note(
                allow_custom=True,
                id=self.generate_id(
                    Note,
                    **{self.X_SOURCE_ID: note.id},
                ),
                abstract=note.name,
                content=note.description,
                note_types=note.note_types,
                authors=[
                    author_ref
                    for contributor in note.contributors
                    if (author_ref := self._get_identity_by_ref(contributor))
                ],
                object_refs=[
                    object_ref
                    for related_id in note.related_ids
                    if (object_ref := self._get_object_ref(related_id))
                ],
                external_references=note.model_dump(
                    mode="json", include=(_ := "external_references")
                )[_],
                object_marking_refs=self.marking_definitions,
                confidence=100,
                created_by_ref=self._get_created_by_ref(*note.contributors),
                custom_properties={
                    "x_mitre_contributors": list(
                        set(
                            self._get_contributor_name(contributor)
                            for contributor in note.contributors
                        )
                    ),
                    self.X_SOURCE_ID: note.id,
                },
            )
            for note in self.bundle.notes
        ]

    @cached_property
    def mitre_data_components(self):
        return [
            MitreDataComponent(
                id=self.generate_id(
                    MitreDataComponent,
                    **{self.X_SOURCE_ID: component.id},
                ),
                name=component.name,
                description=component.description,
                external_references=component.model_dump(
                    mode="json", include=(_ := "external_references")
                )[_],
                object_marking_refs=self.marking_definitions,
                confidence=100,
                created_by_ref=self._get_created_by_ref(*component.contributors),
                custom_properties={
                    "x_mitre_contributors": list(
                        set(
                            self._get_contributor_name(contributor)
                            for contributor in component.contributors
                        )
                    ),
                    "x_mitre_data_source_ref": self._get_data_source_ref(
                        component.parent_id
                    ),
                    self.X_SOURCE_ID: component.id,
                },
            )
            for component in self.bundle.detection_components
        ]

    @cached_property
    def mitre_data_sources(self):
        return [
            MitreDataSource(
                id=self.generate_id(
                    MitreDataSource,
                    **{self.X_SOURCE_ID: source.id},
                ),
                name=source.name,
                description=source.description,
                external_references=source.model_dump(
                    mode="json", include=(_ := "external_references")
                )[_],
                object_marking_refs=self.marking_definitions,
                confidence=100,
                created_by_ref=self._get_created_by_ref(*source.contributors),
                custom_properties={
                    "x_mitre_collection_layers": source.collection_layers,
                    "x_mitre_contributors": list(
                        set(
                            self._get_contributor_name(contributor)
                            for contributor in source.contributors
                        )
                    ),
                    "x_mitre_platforms": source.platforms,
                    self.X_SOURCE_ID: source.id,
                },
            )
            for source in self.bundle.detection_sources
        ]

    @cached_property
    def mitre_tactics(self):
        return [
            MitreTactic(
                id=self.generate_id(
                    MitreTactic,
                    **{self.X_SOURCE_ID: tactic.id},
                ),
                name=tactic.name,
                description=tactic.description,
                external_references=tactic.model_dump(
                    mode="json", include=(_ := "external_references")
                )[_],
                object_marking_refs=self.marking_definitions,
                confidence=100,
                created_by_ref=self._get_created_by_ref(*tactic.contributors),
                custom_properties={
                    "x_mitre_contributors": list(
                        set(
                            self._get_contributor_name(contributor)
                            for contributor in tactic.contributors
                        )
                    ),
                    "x_mitre_shortname": tactic.name,
                    self.X_SOURCE_ID: tactic.id,
                },
            )
            for tactic in self.bundle.tactics
        ]

    @cached_property
    def mitre_matrix(self):
        return MitreMatrix(
            allow_custom=True,
            id=self.generate_id(
                MitreMatrix,
                **{self.X_SOURCE_ID: self.bundle.source},
            ),
            name=self.bundle.name,
            description=self.bundle.description,
            tactic_refs=self.mitre_tactics,
            object_marking_refs=self.marking_definitions,
            confidence=100,
            # Do not use `self._get_created_by_ref` which will cause an infinite loop.
            created_by_ref=self.DEFAULT_AUTHOR["id"],
        )

    @cached_property
    def relationships(self):
        relationships: list[Relationship] = []  # type: ignore[annotation-unchecked]
        for technique in self.bundle.techniques:
            if attack_pattern_id := self._get_attacked_by_ref(technique.id):
                relationships.extend(
                    Relationship(
                        id=self.generate_id(
                            Relationship,
                            relationship_type=(relationship_type := "uses"),
                            source_ref=tool_id,
                            target_ref=attack_pattern_id,
                        ),
                        source_ref=tool_id,
                        target_ref=attack_pattern_id,
                        description=_.description,
                        relationship_type=relationship_type,
                        created_by_ref=self._get_created_by_ref(
                            *technique.contributors
                        ),
                        object_marking_refs=self.marking_definitions,
                    )
                    for _ in technique.tools
                    if (tool_id := self._get_tool_by_ref(_.id))
                )
                relationships.extend(
                    Relationship(
                        id=self.generate_id(
                            Relationship,
                            relationship_type=(relationship_type := "mitigates"),
                            source_ref=course_of_action_id,
                            target_ref=attack_pattern_id,
                        ),
                        source_ref=course_of_action_id,
                        target_ref=attack_pattern_id,
                        description=_.description,
                        relationship_type=relationship_type,
                        created_by_ref=self._get_created_by_ref(
                            *technique.contributors
                        ),
                        object_marking_refs=self.marking_definitions,
                    )
                    for _ in technique.mitigations
                    if (course_of_action_id := self._get_mitigated_by_ref(_.id))
                )
                if technique.detection:
                    relationships.extend(
                        Relationship(
                            allow_custom=True,
                            id=self.generate_id(
                                Relationship,
                                relationship_type=(relationship_type := "detects"),
                                source_ref=data_component_id,
                                target_ref=attack_pattern_id,
                            ),
                            source_ref=data_component_id,
                            target_ref=attack_pattern_id,
                            relationship_type=relationship_type,
                            description=_.description,
                            created_by_ref=self._get_created_by_ref(
                                *technique.contributors
                            ),
                            object_marking_refs=self.marking_definitions,
                        )
                        for _ in technique.detection.items
                        if (data_component_id := self._get_data_component_ref(_.id))
                    )
                if technique.parent_id and (
                    parent_id := self._get_attacked_by_ref(technique.parent_id)
                ):
                    relationships.append(
                        Relationship(
                            id=self.generate_id(
                                Relationship,
                                relationship_type=(
                                    relationship_type := "subtechnique-of"
                                ),
                                source_ref=attack_pattern_id,
                                target_ref=parent_id,
                            ),
                            source_ref=attack_pattern_id,
                            target_ref=parent_id,
                            relationship_type=relationship_type,
                            created_by_ref=self._get_created_by_ref(
                                *technique.contributors
                            ),
                            object_marking_refs=self.marking_definitions,
                        )
                    )

        return relationships

    @cache
    def _get_attacked_by_ref(self, technique_id: str):
        for attack_pattern in self.attack_patterns:
            if technique_id == attack_pattern[self.X_SOURCE_ID]:
                return cast(str, attack_pattern["id"])

    @cache
    def _get_created_by_ref(self, *contributors: str):
        """Returns the first matching contributors as the author.

        If not found return the default value.
        """
        for identity in self.identities:
            if any(
                contributor == identity[self.X_SOURCE_ID]
                or contributor == identity["name"]
                for contributor in contributors
            ):
                return cast(str, identity["id"])
        else:
            return cast(str, self.DEFAULT_AUTHOR["id"])

    @cache
    def _get_contributor_name(self, contributor: str):
        """Returns the first matching identity name.

        If not found return the original input.
        """
        for identity in self.identities:
            if (
                contributor == identity[self.X_SOURCE_ID]
                or contributor == identity["name"]
            ):
                return cast(str, identity["name"])
        else:
            return contributor

    @cache
    def _get_data_component_ref(self, component_id: str):
        for data_component in self.mitre_data_components:
            if component_id == data_component[self.X_SOURCE_ID]:
                return cast(str, data_component["id"])

    @cache
    def _get_data_source_ref(self, source_id: str):
        for data_source in self.mitre_data_sources:
            if source_id == data_source[self.X_SOURCE_ID]:
                return cast(str, data_source["id"])

    @cache
    def _get_identity_by_ref(self, identity_id: str):
        for identity in self.identities:
            if identity_id == identity[self.X_SOURCE_ID]:
                return cast(str, identity["id"])

    @cache
    def _get_mitigated_by_ref(self, mitigation_id: str):
        for course_of_action in self.course_of_actions:
            if mitigation_id == course_of_action[self.X_SOURCE_ID]:
                return cast(str, course_of_action["id"])

    @cache
    def _get_object_ref(self, object_id: str):
        match ((__ := re.match(r"[A-Z]+", object_id)) and __.group()):
            case "D":
                if "." in object_id:
                    return self._get_data_component_ref(object_id)
                else:
                    return self._get_data_source_ref(object_id)
            case "M":
                return self._get_mitigated_by_ref(object_id)
            case "T":
                return self._get_attacked_by_ref(object_id)
            case "TL":
                return self._get_tool_by_ref(object_id)
            case _:
                return None

    @cache
    def _get_tool_by_ref(self, tool_id: str):
        for tool in self.tools:
            if tool_id == tool[self.X_SOURCE_ID]:
                return cast(str, tool["id"])


class Markdown:

    def __init__(self, bundle: Bundle):
        self.bundle = bundle

    @property
    def home_page(self):
        groups, subgroups = defaultdict(list[dict]), defaultdict(list[dict])
        for technique in self.bundle.techniques:
            if not technique.parent_id:
                groups[technique.tactic_id].append(technique.model_dump())
            else:
                subgroups[technique.parent_id].append(technique.model_dump())
        else:
            _phases_row, _tactics_row = "", ""
            _techniques_rows = [""] * max(0, 0, *(len(_) for _ in groups.values()))
        for phase in self.bundle.phases:
            _tactics_cells = []
            for tactic in self.bundle.tactics:
                if tactic.phase_id == phase.id:
                    for idx in range(len(_techniques_rows)):
                        _techniques_rows[idx] += "\n" + " " * 20
                        if idx < len(_ := groups.get(tactic.id)) and (
                            technique := _[idx]
                        ):
                            if subtechniques := subgroups.get(technique.get("id")):
                                _techniques_rows[idx] += self._format(
                                    "<td>"
                                    f"\n{(" " * 24)}<details>"
                                    f"\n{(" " * 24)}<summary>"
                                    '<a title="{id}" href="{{% link {techniques_folder}/{id}.md %}}">'
                                    "{id}:<br>{name}"
                                    "</a></summary>"
                                    f"\n{(" " * 24)}<div>\n{(" " * 28)}"
                                    + f"\n{(" " * 28)}".join(
                                        "<div>"
                                        f'<a title="{{subtechniques[{__}][id]}}" '
                                        f'href="{{{{% link {{techniques_folder}}/{{subtechniques[{__}][id]}}.md %}}}}">'
                                        f"{{subtechniques[{__}][id]}}:<br>{{subtechniques[{__}][name]}}"
                                        "</a>"
                                        "</div>"
                                        for __ in range(len(subtechniques))
                                    )
                                    + f"\n{(" " * 24)}</div>"
                                    f"\n{(" " * 24)}</details>"
                                    "</td>",
                                    technique,
                                    subtechniques=subtechniques,
                                )
                            else:
                                _techniques_rows[idx] += self._format(
                                    "<td>"
                                    '<a title="{id}" href="{{% link {techniques_folder}/{id}.md %}}">'
                                    "{id}:<br>{name}"
                                    "</a>"
                                    "</td>",
                                    technique,
                                )
                        else:
                            _techniques_rows[idx] += "<td></td>"
                    else:
                        _tactics_cells.append(
                            self._format(
                                "<th>"
                                '<a title="{id}" href="{{% link {tactics_folder}/{id}.md %}}">'
                                "{id}:<br>{name}"
                                "</a>"
                                "</th>",
                                tactic.model_dump(),
                            )
                        )
                else:
                    continue
            else:
                _phases_row += (
                    "\n"
                    + " " * 20
                    + self._format(
                        '<th colspan="{colspan}">'
                        '<a title="{id}" href="{{% link {phases_folder}/{id}.md %}}">{name}</a>'
                        "</th>",
                        phase.model_dump(),
                        colspan=(len(_tactics_cells)) or 1,
                    )
                )
                _tactics_row += (
                    "\n"
                    + " " * 20
                    + (("\n" + " " * 20).join(_tactics_cells) or "<th></th>")
                )
                if not _tactics_cells:
                    for idx in range(len(_techniques_rows)):
                        _techniques_rows[idx] += "\n" + " " * 20 + "<td></td>"

        yield (
            self.bundle.subpath(),
            f"""---
title: {"攻擊矩陣" if self.bundle.is_root else "📥"}
order: 100
---

{self.bundle.description}

當前版本: **{VERSION}**

<a href="{{% link {self.bundle.filename} %}}" download>
    <button><kbd>下載 STIX 格式檔案</kbd></button>
</a>
<div class="border-light text-center">
    <div>
        {self.bundle.source} 矩陣 -
        <span title="Tactics, Techniques, and Procedures (TTPs)">
            戰術、技術與程序
        </span>
    </div>
    <div class="table-responsive">
        <table>
            <thead>
                <tr>{_phases_row}
                </tr>
                <tr>{_tactics_row}
                </tr>
            </thead>
            <tbody>
                {"\n" + " " * 16 if _techniques_rows else ""}{
                ("\n" + " " * 16).join(f"<tr>{_}\n{(" " * 16)}</tr>" for _ in _techniques_rows)}
            </tbody>
        </table>
    </div>
</div>
""",
        )

    @property
    def contributors_pages(self):
        if not len(self.bundle.contributors):
            return

        index_lines = [
            "---",
            "title: 貢獻者",
            "order: 8",
            "---",
            "",
            "| 編號 | 名稱 | 簡介 |",
            "| - | - | - |",
        ]
        for contributor in self.bundle.contributors:
            index_lines.append(
                self._format(
                    "| [{id}]({id}) | {name} | {description} |",
                    contributor.model_dump(),
                    truncate=True,
                )
            )
            yield (
                contributor.filepath,
                self._format(
                    """---
title: "{name}"
---

{lables}

### 摘要

{description}

### 聯絡資訊

{contact}
"""
                    + self._table_of_contents_references(contributor),
                    contributor.model_dump(),
                    lables=" ".join(
                        f"`{_}`"
                        for _ in [
                            contributor.id.upper(),
                            contributor.type.displayname,
                            (contributor.firstname or "")
                            + (contributor.lastname or ""),
                            (
                                contributor.organization_type.value.upper()
                                if contributor.organization_type
                                else ""
                            ),
                        ]
                        + [_.value.upper() for _ in contributor.sectors]
                        if _
                    ),
                ),
            )
        else:
            index_lines.append("")
            yield (self.bundle.subpath("contributors"), "\n".join(index_lines))

    @property
    def detections_pages(self):
        if not len(self.bundle.detection_sources):
            return

        index_lines = [
            "---",
            "title: 偵測資源",
            "order: 4",
            "---",
            "",
            "| 編號 | 名稱 | 簡介 |",
            "| - | - | - |",
        ]
        for source in self.bundle.detection_sources:
            index_lines.append(
                self._format(
                    "| [{id}]({id}) | {name} | {description} |",
                    source.model_dump(),
                    truncate=True,
                )
            )
            component_lines = [
                f"| [{component.name}]({{{{% link {{detection_components_folder}}/{component.id}.md %}}}}) "
                f"| {html.escape(component.description or _BLANK).split("\n", 1)[0].strip()} |"
                for component in self.bundle.detection_components
                if component.parent_id == source.id
            ]
            if component_lines:
                component_lines = [
                    "| 項目 | 描述 |",
                    "| - | - |",
                ] + component_lines

            yield (
                source.filepath,
                self._format(
                    """---
title: "偵測來源 {id}: {name}"
---
"""
                    + (
                        "\n* **平台**:\n"
                        + "、".join(f"`{_.value.upper()}`" for _ in source.platforms)
                        + "\n"
                        if source.platforms
                        else ""
                    )
                    + (
                        "\n* **收集層**:\n"
                        + "、".join(
                            f"`{_.value.upper()}`" for _ in source.collection_layers
                        )
                        + "\n"
                        if source.collection_layers
                        else ""
                    )
                    + """
### 摘要

{description}
"""
                    + (
                        "\n### 資料元件\n\n" + "\n".join(component_lines) + "\n"
                        if component_lines
                        else ""
                    )
                    + self._table_of_contents_references(source),
                    source.model_dump(),
                ),
            )
        else:
            index_lines.append("")
            yield (self.bundle.subpath("detection_sources"), "\n".join(index_lines))

        # Data sources also include data components
        for component in self.bundle.detection_components:
            technique_lines = [
                f"| [{technique.name}]({{{{% link {{techniques_folder}}/{technique.id}.md %}}}}) "
                f"| {html.escape(_ or _BLANK).split("\n", 1)[0].strip()} |"
                for technique, _ in self.bundle.get_techniques(
                    component_id=component.id
                )
            ]
            if technique_lines:
                technique_lines = [
                    "| 技術 | 偵測到 |",
                    "| - | - |",
                ] + technique_lines

            yield (
                component.filepath,
                self._format(
                    """---
title: "偵測元件 {id}: {name}"
---

* **資料來源**:
[{parent_id}]({{% link {detection_sources_folder}/{parent_id}.md %}})

### 摘要

{description}
"""
                    + (
                        "\n### 發現的技術\n\n" + "\n".join(technique_lines) + "\n"
                        if technique_lines
                        else ""
                    )
                    + self._table_of_contents_references(component),
                    component.model_dump(),
                ),
            )

    @property
    def mitigations_pages(self):
        if not len(self.bundle.mitigations):
            return

        index_lines = [
            "---",
            "title: 緩解措施",
            "order: 5",
            "---",
            "",
            "| 編號 | 名稱 | 簡介 |",
            "| - | - | - |",
        ]
        for mitigation in self.bundle.mitigations:
            index_lines.append(
                self._format(
                    "| [{id}]({id}) | {name} | {description} |",
                    mitigation.model_dump(),
                    truncate=True,
                )
            )

            technique_lines = [
                f"| [{technique.name}]({{{{% link {{techniques_folder}}/{technique.id}.md %}}}}) "
                f"| {html.escape(_ or _BLANK).split("\n", 1)[0].strip()} |"
                for technique, _ in self.bundle.get_techniques(
                    mitigation_id=mitigation.id
                )
            ]
            if technique_lines:
                technique_lines = [
                    "| 技術 | 用例 |",
                    "| - | - |",
                ] + technique_lines

            yield (
                mitigation.filepath,
                self._format(
                    """---
title: "緩解措施 {id}: {name}"
---

### 摘要

{description}
"""
                    + (
                        "\n### 解決的技術\n\n" + "\n".join(technique_lines) + "\n"
                        if technique_lines
                        else ""
                    )
                    + self._table_of_contents_references(mitigation),
                    mitigation.model_dump(),
                ),
            )
        else:
            index_lines.append("")
            yield (self.bundle.subpath("mitigations"), "\n".join(index_lines))

    @property
    def notes_pages(self):
        if not len(self.bundle.notes):
            return

        index_lines = [
            "---",
            "title: 筆記",
            "order: 7",
            "---",
            "",
            "| 編號 | 標題 | 內容 |",
            "| - | - | - |",
        ]
        for note in self.bundle.notes:
            index_lines.append(
                self._format(
                    "| [{id}]({id}) | {name} | {description} |",
                    note.model_dump(),
                    truncate=True,
                )
            )

            technique_lines = [
                f"| [{_.name}]({{{{% link {{techniques_folder}}/{_.id}.md %}}}}) "
                f"| {html.escape(_.description or _BLANK).split("\n", 1)[0].strip()} |"
                for _ in self.bundle.techniques
                if _.id in note.related_ids
            ]
            if technique_lines:
                technique_lines = [
                    "| 項目 | 描述 |",
                    "| - | - |",
                ] + technique_lines

            mitigation_lines = [
                f"| [{_.name}]({{{{% link {{mitigations_folder}}/{_.id}.md %}}}}) "
                f"| {html.escape(_.description or _BLANK).split("\n", 1)[0].strip()} |"
                for _ in self.bundle.mitigations
                if _.id in note.related_ids
            ]
            if mitigation_lines:
                mitigation_lines = [
                    "| 項目 | 描述 |",
                    "| - | - |",
                ] + mitigation_lines

            detection_lines = [
                f"| [{_.name}]({{{{% link {{detection_sources_folder}}/{_.id}.md %}}}}) "
                f"| {html.escape(_.description or _BLANK).split("\n", 1)[0].strip()} |"
                for _ in sorted(
                    self.bundle.detection_sources + self.bundle.detection_components,
                    key=attrgetter("id"),
                )
                if _.id in note.related_ids
            ]
            if detection_lines:
                detection_lines = [
                    "| 項目 | 描述 |",
                    "| - | - |",
                ] + detection_lines

            tool_lines = [
                f"| [{_.name}]({{{{% link {{techniques_folder}}/{_.id}.md %}}}}) "
                f"| {html.escape(_.description or _BLANK).split("\n", 1)[0].strip()} |"
                for _ in self.bundle.tools
                if _.id in note.related_ids
            ]
            if tool_lines:
                tool_lines = [
                    "| 項目 | 描述 |",
                    "| - | - |",
                ] + tool_lines

            yield (
                note.filepath,
                self._format(
                    """---
title: "筆記 {id}: {name}"
---
"""
                    + (
                        "\n* **筆記類型**:\n"
                        + "、".join(f"`{_.value.upper()}`" for _ in note.note_types)
                        + "\n"
                        if note.note_types
                        else ""
                    )
                    + """
### 內容

{description}
"""
                    + (
                        "\n### 被應用的技術\n\n" + "\n".join(technique_lines) + "\n"
                        if technique_lines
                        else ""
                    )
                    + (
                        "\n### 關聯的緩解措施\n\n" + "\n".join(mitigation_lines) + "\n"
                        if mitigation_lines
                        else ""
                    )
                    + (
                        "\n### 關聯的偵測資源\n\n" + "\n".join(detection_lines) + "\n"
                        if detection_lines
                        else ""
                    )
                    + (
                        "\n### 被應用的工具\n\n" + "\n".join(tool_lines) + "\n"
                        if tool_lines
                        else ""
                    )
                    + self._table_of_contents_references(note),
                    note.model_dump(),
                ),
            )
        else:
            index_lines.append("")
            yield (self.bundle.subpath("notes"), "\n".join(index_lines))

    @property
    def phases_pages(self):
        if not len(self.bundle.phases):
            return

        index_lines = [
            "---",
            "title: 階段",
            "order: 1",
            "---",
            "",
            "| 編號 | 名稱 | 簡介 |",
            "| - | - | - |",
        ]
        for phase in self.bundle.phases:
            index_lines.append(
                self._format(
                    "| [{id}]({id}) | {name} | {description} |",
                    phase.model_dump(),
                    truncate=True,
                )
            )

            tactic_lines = [
                f"| [{tactic.name}]({{{{% link {{tactics_folder}}/{tactic.id}.md %}}}}) "
                f"| {html.escape(tactic.description or _BLANK).split("\n", 1)[0].strip()} |"
                for tactic in self.bundle.get_tactics(phase_id=phase.id)
            ]
            if tactic_lines:
                tactic_lines = [
                    "| 戰術 | 說明 |",
                    "| - | - |",
                ] + tactic_lines

            yield (
                phase.filepath,
                self._format(
                    """---
title: "階段 {id}: {name}"
---

### 摘要

{description}
"""
                    + (
                        "\n### 附屬的戰術\n\n" + "\n".join(tactic_lines) + "\n"
                        if tactic_lines
                        else ""
                    )
                    + self._table_of_contents_references(phase),
                    phase.model_dump(),
                ),
            )
        else:
            index_lines.append("")
            yield (self.bundle.subpath("phases"), "\n".join(index_lines))

    @property
    def tactics_pages(self):
        if not len(self.bundle.tactics):
            return

        index_lines = [
            "---",
            "title: 戰術",
            "order: 2",
            "---",
            "",
            "| 編號 | 名稱 | 簡介 | 階段編號 |",
            "| - | - | - | - |",
        ]
        for tactic in self.bundle.tactics:
            index_lines.append(
                self._format(
                    "| [{id}]({id}) | {name} | {description} | "
                    "[{phase_id}]({{% link {phases_folder}/{phase_id}.md %}}) |",
                    tactic.model_dump(),
                    truncate=True,
                )
            )

            technique_lines = [
                f"| [{technique.name}]({{{{% link {{techniques_folder}}/{technique.id}.md %}}}}) "
                f"| {html.escape(technique.description or _BLANK).split("\n", 1)[0].strip()} |"
                for technique in self.bundle.get_techniques(tactic_id=tactic.id)
            ]
            if technique_lines:
                technique_lines = [
                    "| 技術 | 說明 |",
                    "| - | - |",
                ] + technique_lines

            yield (
                tactic.filepath,
                self._format(
                    """---
title: "戰術 {id}: {name}"
---

* **屬於**:
[{phase_name}]({{% link {phases_folder}/{phase_id}.md %}})

### 摘要

{description}
"""
                    + (
                        "\n### 附屬的技術\n\n" + "\n".join(technique_lines) + "\n"
                        if technique_lines
                        else ""
                    )
                    + self._table_of_contents_references(tactic),
                    tactic.model_dump(),
                    phase_name=(
                        _.name
                        if (_ := self.bundle.get_phase(tactic.phase_id))
                        else tactic.phase_id
                    ),
                ),
            )
        else:
            index_lines.append("")
            yield (self.bundle.subpath("tactics"), "\n".join(index_lines))

    @property
    def techniques_pages(self):
        if not len(self.bundle.techniques):
            return

        index_lines = [
            "---",
            "title: 技術",
            "order: 3",
            "---",
            "",
            "| 編號 | 名稱 | 簡介 | 戰術編號 |",
            "| - | - | - | - |",
        ]
        for technique in self.bundle.techniques:
            index_lines.append(
                self._format(
                    "| [{id}]({id}) | {name} | {description} | "
                    "[{tactic_id}]({{% link {tactics_folder}/{tactic_id}.md %}}) |",
                    technique.model_dump(),
                    truncate=True,
                )
            )

            tool_lines = [
                f"| [{tool.name}]({{{{% link {{tools_folder}}/{tool.id}.md %}}}}) "
                f"| {html.escape(_.description or tool.description or _BLANK).split("\n", 1)[0].strip()} |"
                for _ in technique.tools
                if (tool := self.bundle.get_tool(_.id))
            ]
            if tool_lines:
                tool_lines = [
                    "| 項目 | 描述 |",
                    "| - | - |",
                ] + tool_lines

            mitigation_lines = [
                f"| [{mitigation.name}]({{{{% link {{mitigations_folder}}/{mitigation.id}.md %}}}}) "
                f"| {html.escape(_.description or mitigation.description or _BLANK).split("\n", 1)[0].strip()} |"
                for _ in technique.mitigations
                if (mitigation := self.bundle.get_mitigation(_.id))
            ]
            if mitigation_lines:
                mitigation_lines = [
                    "| 項目 | 描述 |",
                    "| - | - |",
                ] + mitigation_lines

            component_lines = [
                f"| [{source.name}]({{{{% link {{detection_sources_folder}}/{source.id}.md %}}}}) "
                f"| [{component.name}]({{{{% link {{detection_components_folder}}/{component.id}.md %}}}}) "
                f"| {html.escape(_.description or component.description or _BLANK).split("\n", 1)[0].strip()} |"
                for _ in technique.detection.items
                if (component := self.bundle.get_detection_component(_.id))
                and (source := self.bundle.get_detection_source(component.parent_id))
            ]
            if component_lines:
                component_lines = [
                    "| 資料來源 | 資料元件 | 偵測到 |",
                    "| - | - | - |",
                ] + component_lines

            subtechnique_lines = [
                "  <details><summary>"
                f'<a title="{subtechnique.id}" href="{{{{% link {{techniques_folder}}/{subtechnique.id}.md %}}}}">'
                f"{subtechnique.name}</a></summary>"
                f"<p>&emsp;&emsp;{html.escape(subtechnique.description or _BLANK).split("\n", 1)[0].strip()}</p>"
                "</details>"
                for subtechnique in self.bundle.get_techniques(parent_id=technique.id)
            ]

            yield (
                technique.filepath,
                self._format(
                    """---
title: "技術 {id}: {name}"
---

* **戰術階段**:
[{tactic_name}]({{% link {tactics_folder}/{tactic_id}.md %}})
"""
                    + (
                        "\n* **上層技術**:\n[{parent_name}]({parent_id})\n"
                        if technique.parent_id
                        else ""
                    )
                    + (
                        "\n* **子技術**:\n\n" + "\n".join(subtechnique_lines) + "\n"
                        if subtechnique_lines
                        else ""
                    )
                    + (
                        "\n* **平台**:\n"
                        + "、".join(f"`{_.value.upper()}`" for _ in technique.platforms)
                        + "\n"
                        if technique.platforms
                        else ""
                    )
                    + (
                        "\n* **所需權限**:\n"
                        + "、".join(
                            f"`{_.value.upper()}`" for _ in technique.permissions
                        )
                        + "\n"
                        if technique.permissions
                        else ""
                    )
                    + """
### 摘要

{description}
"""
                    + (
                        "\n### 工具\n\n" + "\n".join(tool_lines) + "\n"
                        if tool_lines
                        else ""
                    )
                    + (
                        "\n### 緩解措施\n\n" + "\n".join(mitigation_lines) + "\n"
                        if mitigation_lines
                        else ""
                    )
                    + (
                        "\n### 偵測資訊\n\n"
                        + (
                            "{detection[description]}\n\n"
                            if technique.detection.description
                            else ""
                        )
                        + "\n".join(component_lines)
                        + "\n"
                        if technique.detection.description or component_lines
                        else ""
                    )
                    + self._table_of_contents_references(technique),
                    technique.model_dump(),
                    parent_name=(
                        _.name
                        if (_ := self.bundle.get_technique(technique.parent_id))
                        else technique.parent_id
                    ),
                    tactic_name=(
                        _.name
                        if (_ := self.bundle.get_tactic(technique.tactic_id))
                        else technique.tactic_id
                    ),
                ),
            )
        else:
            index_lines.append("")
            yield (self.bundle.subpath("techniques"), "\n".join(index_lines))

    def _format(self, template: str, data: dict = {}, *, truncate=False, **kwargs):
        data.update(self.bundle.subfolder_mapping, **kwargs)
        return template.format_map(
            defaultdict(
                lambda: _BLANK,
                **{
                    k: (
                        html.escape(
                            v.split("\n", 1)[0].strip() or _BLANK if truncate else v
                        )
                        if isinstance(v, str)
                        else v
                    )
                    for k, v in data.items()
                    if v not in ("", None)
                },
            )
        )

    def _table_of_contents_references(self, data: Base):
        return (
            (
                "\n### 參考資料\n\n"
                + "\n".join(
                    idx_str
                    + (
                        f"[{title}]({external_reference.url})"
                        if external_reference.url
                        else title
                    )
                    for idx, external_reference in enumerate(
                        data.external_references[1:], start=1
                    )
                    if (
                        title := html.escape(
                            external_reference.description
                            or (
                                f"{external_reference.source_name} ({external_reference.external_id})"
                                if external_reference.external_id
                                else external_reference.source_name
                            )
                        ).replace("\n", f"\n{" " * len(idx_str := f"{idx}. ")}")
                    )
                )
                + "\n"
            )
            if 1 < len(data.external_references)
            else ""
        )

    @property
    def tools_pages(self):
        if not len(self.bundle.tools):
            return

        index_lines = [
            "---",
            "title: 工具",
            "order: 6",
            "---",
            "",
            "| 編號 | 名稱 | 簡介 |",
            "| - | - | - |",
        ]
        for tool in self.bundle.tools:
            index_lines.append(
                self._format(
                    "| [{id}]({id}) | {name} | {description} |",
                    tool.model_dump(),
                    truncate=True,
                )
            )

            technique_lines = [
                f"| [{technique.name}]({{{{% link {{techniques_folder}}/{technique.id}.md %}}}}) "
                f"| {html.escape(_ or _BLANK).split("\n", 1)[0].strip()} |"
                for technique, _ in self.bundle.get_techniques(tool_id=tool.id)
            ]
            if technique_lines:
                technique_lines = [
                    "| 技術 | 用例 |",
                    "| - | - |",
                ] + technique_lines

            yield (
                tool.filepath,
                self._format(
                    """---
title: "工具 {id}: {name}"
---
"""
                    + (
                        "\n* **平台**:\n"
                        + "、".join(f"`{_.value.upper()}`" for _ in tool.platforms)
                        + "\n"
                        if tool.platforms
                        else ""
                    )
                    + (
                        "\n* **工具類型**:\n"
                        + "、".join(f"`{_.value.upper()}`" for _ in tool.tool_types)
                        + "\n"
                        if tool.tool_types
                        else ""
                    )
                    + ("\n* **工具版本**:{tool_version}\n" if tool.tool_version else "")
                    + """
### 摘要

{description}
"""
                    + (
                        "\n### 使用的技術\n\n" + "\n".join(technique_lines) + "\n"
                        if technique_lines
                        else ""
                    )
                    + self._table_of_contents_references(tool),
                    tool.model_dump(),
                ),
            )
        else:
            index_lines.append("")
            yield (self.bundle.subpath("tools"), "\n".join(index_lines))


class Parser:

    def __init__(self, **kwargs):
        self.bundle = Bundle(kwargs)
        self.stix = Stix(self.bundle)
        self.markdown = Markdown(self.bundle)

    def to_stix(self) -> str:
        """Fetch JSON-formatted SITX bundle objects file.

        .. seealso::
            :py:meth:`stix2.MemoryStore.save_to_file` - Write SITX objects to JSON file, as a STIX Bundle.

        :return: Path of bundle file
        """
        memory_store = MemoryStore()
        memory_store.add(self.stix.marking_definitions)
        memory_store.add(self.stix.identities)
        memory_store.add(self.stix.attack_patterns)
        memory_store.add(self.stix.course_of_actions)
        memory_store.add(self.stix.tools)
        memory_store.add(self.stix.notes)
        memory_store.add(self.stix.relationships)
        memory_store.add(self.stix.mitre_data_components)
        memory_store.add(self.stix.mitre_data_sources)
        memory_store.add(self.stix.mitre_tactics)
        memory_store.add(self.stix.mitre_matrix)
        return memory_store.save_to_file(self.bundle.filepath)

    def to_markdown(self):
        """Fetch Markdown-formatted documents of the framework according to the bundle data.

        :return: Storage path and content of each file"""
        yield from self.markdown.home_page
        # yield from self.markdown.contributors_pages
        yield from self.markdown.detections_pages
        yield from self.markdown.mitigations_pages
        yield from self.markdown.notes_pages
        yield from self.markdown.phases_pages
        yield from self.markdown.tactics_pages
        yield from self.markdown.techniques_pages
        yield from self.markdown.tools_pages
