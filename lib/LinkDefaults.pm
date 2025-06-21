package LinkDefaults;
use strict;
use warnings;
use Exporter 'import';
use JSON::PP qw(decode_json);

our @EXPORT_OK = qw(load_defaults);

sub load_defaults {
    my ($path) = @_;
    open my $fh, '<', $path or die "Cannot open $path: $!";
    local $/;
    my $json = <$fh>;
    close $fh;
    return decode_json($json);
}

1;
