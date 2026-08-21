# DDO#451 material intake adapter — FDE

Центральный канон: https://github.com/sevranty/design-director-ops/blob/main/06_governance/finuslugi_material_intake_fanout_contract.md

Rollout: https://github.com/sevranty/design-director-ops/issues/492

При `DDO#451 DELIVERY_MATRIX = WRITE` FDE child Issue обязана получить `MATERIAL_UMBRELLA`, `FDO_SOURCE_ID`, `FDO_SOURCE_URL`, `FDO_SOURCE_FINGERPRINT` и source classification.

FDE строит только repository-owned normalized digest/editorial/redpolicy evidence и skill-input projection. Этот adapter сам по себе не разрешает менять runtime, `SKILL.md`, reference behavior или production. Каждый derived object связан с FDO canonical source и DDO material umbrella.

`LINK`, `TRANSFER` и `NOT_APPLICABLE` не дают write permission. Finuslugi original/source owner — FDO.
