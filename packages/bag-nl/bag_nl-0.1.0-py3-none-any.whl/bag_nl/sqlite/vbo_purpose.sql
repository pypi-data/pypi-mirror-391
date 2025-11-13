CREATE TABLE bag_vbo_purpose (
    vbo integer,
    purpose integer
) strict;

CREATE INDEX bag_vbo_purpose_idx_vbo on bag_vbo_purpose (vbo);
