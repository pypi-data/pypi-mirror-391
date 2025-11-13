CREATE TABLE bag_wpl (
    id integer primary key,
    name text,
    geo text,
    tile text,
    date integer
) strict;

CREATE INDEX bag_wpl_idx_name on bag_wpl (name);
CREATE INDEX bag_wpl_idx_tile on bag_wpl (tile);
