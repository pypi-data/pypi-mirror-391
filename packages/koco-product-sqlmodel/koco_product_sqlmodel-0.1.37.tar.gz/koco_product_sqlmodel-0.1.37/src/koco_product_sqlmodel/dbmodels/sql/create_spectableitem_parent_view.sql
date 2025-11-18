CREATE OR REPLACE VIEW spectableitem_parent_view AS
SELECT
    st.parent_id AS parent_id,
    case when st.parent = 'family' then f.family
         when st.parent = 'article' then a.article
         else NULL
    end AS parent_name,
    st.parent AS parent_type,
    st.id AS st_id,
    st.name AS st_name,
    st.type AS st_type,
    sti.id AS sti_id,
    sti.name AS sti_name,
    sti.value AS sti_value
FROM cspectableitem sti
LEFT JOIN cspectable st ON sti.spec_table_id = st.id
LEFT JOIN cfamily f ON st.parent_id = f.id
LEFT JOIN carticle a ON st.parent_id = a.id
WHERE st.parent = 'family' OR st.parent = 'article';
