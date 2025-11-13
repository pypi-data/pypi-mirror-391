CREATE TABLE bag_opr (
    id integer primary key,
    name text,
    type integer,
    status integer,
    wpl integer,
    date integer
) strict;

create index bag_opr_idx_wpl on bag_opr (wpl);
