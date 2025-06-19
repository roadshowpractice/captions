#!/usr/bin/perl
use strict;
use warnings;
use Test::More;
use File::Spec;
use FindBin;
use JSON qw(decode_json encode_json);
use Log::Log4perl;
use File::Path 'make_path';

# Logging setup similar to existing tests
my $log_dir  = File::Spec->catdir($FindBin::Bin, '..', 'logs');
my $log_file = File::Spec->catfile($log_dir, 'acme-frobnitz.log');

unless (-d $log_dir) {
    eval { make_path($log_dir) };
    die "Failed to create log directory $log_dir: $@" if $@;
}

my $log_config = qq(
log4perl.logger                    = INFO, FileAppender
log4perl.appender.FileAppender     = Log::Log4perl::Appender::File
log4perl.appender.FileAppender.filename = $log_file
log4perl.appender.FileAppender.layout   = Log::Log4perl::Layout::PatternLayout
log4perl.appender.FileAppender.layout.ConversionPattern = %d [%p] %m%n
);

Log::Log4perl->init(\$log_config);
my $logger = Log::Log4perl->get_logger();

use lib "$FindBin::Bin/../lib";
use Acme::Frobnitz;

my $metadata_file = File::Spec->catfile($FindBin::Bin, '..', 'metadata', 'test1.json');
open my $fh, '<', $metadata_file or die "Cannot open $metadata_file: $!";
my $json_text = do { local $/; <$fh> };
close $fh;
my $meta = decode_json($json_text);

my $url = $meta->{url} or die "No URL in metadata";
my $frobnitz = Acme::Frobnitz->new();

can_ok('Acme::Frobnitz', 'download');

my $download_out = eval { $frobnitz->download($url) };
if ($@) {
    fail('download threw exception');
    BAIL_OUT($@);
}
else {
    ok($download_out, 'download returned output');
}
my ($downloaded_file) = (split /\n/, $download_out)[-1];
chomp($downloaded_file);
$meta->{tasks}{perform_download} = $downloaded_file;

ok($frobnitz->verify_file($downloaded_file), 'verify download');

my $wm_out = eval { $frobnitz->add_watermark($downloaded_file) };
if ($@) {
    fail('watermark threw exception');
    BAIL_OUT($@);
}
else {
    ok($wm_out, 'watermark returned output');
}
my ($wm_file) = (split /\n/, $wm_out)[-1];
chomp($wm_file);
$meta->{tasks}{apply_watermark} = $wm_file;

# store updated metadata
open my $out, '>', $metadata_file or die "Cannot write $metadata_file: $!";
print $out encode_json($meta);
close $out;

ok(-e $wm_file, 'watermarked file exists');

done_testing();
