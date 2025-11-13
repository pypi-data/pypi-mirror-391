CREATE TABLE bag_wpl_gem (
    wpl integer,
    gem integer
) strict;

CREATE INDEX bag_wpl_gem_idx_wpl on bag_wpl_gem (wpl);
CREATE INDEX bag_wpl_gem_idx_gem on bag_wpl_gem (gem);
