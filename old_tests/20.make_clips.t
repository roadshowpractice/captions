#!/usr/bin/perl
use strict;
use warnings;
use Test::More;
use IPC::Run3 'run3';
use FindBin;
use File::Spec;
use lib "$FindBin::Bin/../lib";
use Acme::Frobnitz;

my $script19 = File::Spec->catfile($FindBin::Bin, '19.download.t');
my ($stdout, $stderr);
run3([$^X, $script19], undef, \$stdout, \$stderr);
my $tap = ($stdout // '') . ($stderr // '');

my ($watermarked_file) = $tap =~ /Watermark added: ([^\n]+)/;
ok($watermarked_file, 'captured watermarked file path');

if ($watermarked_file) {
    my $frobnitz = Acme::Frobnitz->new();
    my $clips_out = eval { $frobnitz->make_clips($watermarked_file) };
    if ($@) {
        fail('make_clips threw exception');
        diag($@);
    } else {
        ok($clips_out, 'make_clips returned output');
    }
}

done_testing;
