CREATE TABLE bag_vbo_pnd (
    vbo integer,
    pnd integer
) strict;

CREATE INDEX bag_vbo_pnd_idx_vbo on bag_vbo_pnd (vbo);
CREATE INDEX bag_vbo_pnd_idx_pnd on bag_vbo_pnd (pnd);
