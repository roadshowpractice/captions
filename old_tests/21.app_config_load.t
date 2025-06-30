#!/usr/bin/perl
use strict;
use warnings;
use Test::More;
use FindBin;
use File::Spec;
use JSON::PP qw(decode_json encode_json);
use File::Temp qw(tempfile);

my $config_path = File::Spec->catfile($FindBin::Bin, '..', 'conf', 'app_config.json');

open my $fh, '<', $config_path or die "Cannot open $config_path: $!";
my $json = do { local $/; <$fh> };
close $fh;

my $config = decode_json($json);

ok( exists $config->{test_url}, 'app_config.json contains test_url' );
ok( !ref $config->{test_url},  'test_url is a scalar value' );

my $url = $config->{test_url};

my ($meta_fh, $meta_file) = tempfile('metaXXXX', SUFFIX => '.json', UNLINK => 1);
print $meta_fh encode_json({ url => $url, tasks => {} });
close $meta_fh;

my $bayardo = File::Spec->catfile($FindBin::Bin, 'bayardo3.t');
my $cmd = join ' ', $^X, $bayardo, $meta_file;
diag("Running bayardo3.t with $meta_file");
system($cmd);
is($?, 0, 'bayardo3.t ran successfully');

done_testing;
