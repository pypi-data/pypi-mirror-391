CREATE TABLE bag_sta (
    id integer primary key,
    num integer,
    status integer,
    geo text,
    tile text,
    date integer
) strict;

CREATE INDEX bag_sta_idx_num on bag_sta (num);
CREATE INDEX bag_sta_idx_tile on bag_sta (tile);
