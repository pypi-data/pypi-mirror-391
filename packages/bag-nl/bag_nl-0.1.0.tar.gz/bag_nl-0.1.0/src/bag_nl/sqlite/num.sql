CREATE TABLE bag_num (
    id integer primary key,
    postcode text,
    number integer,
    extra text,
    letter text,
    type text,
    opr integer,
    date integer
) strict;

CREATE INDEX bag_num_idx_postcode_number on bag_num (postcode, number);
CREATE INDEX bag_num_idx_opr on bag_num (opr);
