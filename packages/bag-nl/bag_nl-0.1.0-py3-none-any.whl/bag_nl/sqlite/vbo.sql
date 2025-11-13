CREATE TABLE bag_vbo (
    id integer primary key,
    num integer,
    geo text,
    area integer,
    tile text,
    date integer
) strict;

CREATE INDEX bag_vbo_idx_num on bag_vbo (num);
CREATE INDEX bag_vbo_idx_tile on bag_vbo (tile);
