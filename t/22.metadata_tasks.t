#!/usr/bin/perl
use strict;
use warnings;
use Test::More;
use FindBin;
use File::Spec;
use JSON::PP qw(decode_json);

my $metadata_dir = File::Spec->catdir($FindBin::Bin, '..', 'metadata');
opendir my $dh, $metadata_dir or die "Cannot open $metadata_dir: $!";
my @json_files = grep { /\.json$/ && -f File::Spec->catfile($metadata_dir, $_) } readdir $dh;
closedir $dh;

plan 'no_plan';

foreach my $file (@json_files) {
    my $path = File::Spec->catfile($metadata_dir, $file);
    open my $fh, '<', $path or die "Cannot open $path: $!";
    my $json_text = do { local $/; <$fh> };
    close $fh;

    my $data = eval { decode_json($json_text) };
    if ($@) {
        diag("Skipping $file: $@");
        next;
    }

    unless (exists $data->{tasks}) {
        diag("Skipping $file: no tasks section");
        next;
    }

    SKIP: {
        skip "$file: perform_download missing", 1
            unless defined $data->{tasks}{perform_download} && length $data->{tasks}{perform_download};
        pass("$file has perform_download");
    }

    SKIP: {
        skip "$file: apply_watermark missing", 1
            unless defined $data->{tasks}{apply_watermark} && length $data->{tasks}{apply_watermark};
        pass("$file has apply_watermark");
    }
}

