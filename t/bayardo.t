#!/usr/bin/perl
use strict;
use warnings;
use Test::More;

# List of URLs to test
my @urls = (
    'https://www.instagram.com/p/DHErSwNhaXp/',
    'https://www.instagram.com/p/DHAO0n5tTG0/',
    'https://www.instagram.com/p/DG_vXnIsb-y/',
    # More URLs can be added here
);

# Setup paths
my $python = '/Users/mymac/miniconda3/envs/new-env/bin/python';
my $script = '/Users/mymac/Desktop/teton/bin/main.py';

# Plan tests dynamically based on URL count
plan tests => scalar(@urls);

foreach my $url (@urls) {
    my $cmd = "$python $script $url";

    # Debug print
    print "\n[TEST] Running command: $cmd\n";

    # Capture output and exit status
    my $output = `$cmd 2>&1`;   # capture stdout and stderr
    my $exit_code = $? >> 8;

    # Show captured output (optional)
    print "[OUTPUT] $output\n";

    # Main check: did the script exit cleanly?
    ok($exit_code == 0, "Successfully processed $url");

    # Extra: if you want to check that output *isn't empty*
    # ok(length($output) > 0, "Got some output from $url");
}
