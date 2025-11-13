CREATE TABLE bag_lig (
    id integer primary key,
    num integer,
    status integer,
    geo text,
    tile text,
    date integer
) strict;

CREATE INDEX bag_lig_idx_num on bag_lig (num);
CREATE INDEX bag_lig_idx_tile on bag_lig (tile);
