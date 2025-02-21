#!/usr/bin/perl

use strict;
use warnings;
use Test::More;
use File::Spec;
use FindBin;
use Cwd 'abs_path';
use Log::Log4perl;
use File::Path 'make_path';
use Acme::Frobnitz;

# Set up logging
my $log_dir = File::Spec->catdir($FindBin::Bin, '..', 'logs');
my $log_file = File::Spec->catfile($log_dir, 'acme-frobnitz.log');

unless (-d $log_dir) {
    eval { make_path($log_dir) };
    die "Failed to create log directory $log_dir: $@" if $@;
}

my $log_config = qq(
log4perl.logger = INFO, FileAppender
log4perl.appender.FileAppender = Log::Log4perl::Appender::File
log4perl.appender.FileAppender.filename = $log_file
log4perl.appender.FileAppender.layout = Log::Log4perl::Layout::PatternLayout
log4perl.appender.FileAppender.layout.ConversionPattern = %d [%p] %m%n
);
Log::Log4perl->init(\$log_config);
my $logger = Log::Log4perl->get_logger();

# Instantiate Frobnitz object
my $frobnitz = Acme::Frobnitz->new();
my $video_url = 'https://www.instagram.com/p/DFy5m4MotA5/';

$logger->info("Starting download for URL: $video_url");
my $download_output = $frobnitz->download($video_url);
my ($last_line) = (split /\n/, $download_output)[-1];
chomp($last_line);

ok($last_line, "Download completed: $last_line");
$logger->info("Downloaded video to: $last_line");

# Verify download
if ($frobnitz->verify_file($last_line)) {
    pass("File verification successful");
    $logger->info("File verification successful");
} else {
    fail("File verification failed");
    $logger->error("File verification failed");
    BAIL_OUT("Verification failed, stopping test.");
}

# Add watermark
$download_output = $frobnitz->add_watermark($last_line);
($last_line) = (split /\n/, $download_output)[-1];
chomp($last_line);
ok($last_line, "Watermark added: $last_line");
$logger->info("Watermark added to: $last_line");

# clips
$download_output = $frobnitz->make_clips($last_line);
($last_line) = (split /\n/, $download_output)[-1];
chomp($last_line);
ok($last_line, "Clips added: $last_line");
$logger->info("Clips added to: $last_line");

done_testing();





