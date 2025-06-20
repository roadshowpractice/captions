#!/usr/bin/perl
use strict;
use warnings;
use Test::More;
use FindBin;
use File::Spec;
use JSON::PP qw(decode_json encode_json);
use File::Temp qw(tempfile);

my $defaults_path = File::Spec->catfile($FindBin::Bin, '..', 'conf', 'link_defaults.json');
open my $fh, '<', $defaults_path or die "Cannot open $defaults_path: $!";
my $json_text = do { local $/; <$fh> };
close $fh;
my $data = decode_json($json_text);

my $insta_link = 'https://www.instagram.com/reel/EXAMPLE/';
$data->{url} = $insta_link;

ok($data->{url} eq $insta_link, 'url field updated with instagram link');

ok(exists $data->{video_download}, 'video_download config present');

ok(exists $data->{tasks}, 'tasks section present');
ok(!defined $data->{tasks}{perform_download}, 'perform_download defaults to undef');
ok(!$data->{tasks}{post_processed}, 'post_processed defaults to false');

my ($tmpfh, $tmpfile) = tempfile('linkXXXX', SUFFIX => '.json', UNLINK => 1);
print $tmpfh encode_json($data);
close $tmpfh;

ok(-e $tmpfile, 'temporary metadata file created');

# Clean up is automatic due to UNLINK => 1

done_testing();
