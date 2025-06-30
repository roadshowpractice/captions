#!/usr/bin/perl
use strict;
use warnings;
use Test::More;
use FindBin;
use File::Spec;
use JSON::PP qw(encode_json);
use lib "$FindBin::Bin/../lib";
use LinkDefaults qw(load_defaults);
use File::Temp qw(tempfile);

my $defaults_path = File::Spec->catfile($FindBin::Bin, '..', 'conf', 'link_defaults.json');
my $data = load_defaults($defaults_path);

my $insta_link = $data->{url};
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
