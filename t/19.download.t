#!/usr/bin/perl

use strict;
use warnings;
use Test::More;
use File::Spec;
use FindBin;
use Cwd 'abs_path';
use Log::Log4perl;
use File::Path 'make_path';
use JSON qw(decode_json);

# Set log directory and file
my $log_dir = File::Spec->catdir($FindBin::Bin, '..', 'logs');
my $log_file = File::Spec->catfile($log_dir, 'acme-frobnitz.log');

# Ensure the logs directory exists
unless (-d $log_dir) {
    eval { make_path($log_dir) };
    if ($@) {
        die "Failed to create log directory $log_dir: $@";
    }
}

# Initialize Log4perl configuration
my $log_config = qq(
log4perl.logger                    = INFO, FileAppender

log4perl.appender.FileAppender     = Log::Log4perl::Appender::File
log4perl.appender.FileAppender.filename = $log_file
log4perl.appender.FileAppender.layout   = Log::Log4perl::Layout::PatternLayout
log4perl.appender.FileAppender.layout.ConversionPattern = %d [%p] %m%n
);

# Initialize Log4perl
Log::Log4perl->init(\$log_config);

# Create logger
my $logger = Log::Log4perl->get_logger();

# Adding the library path relative to this test script
use lib "$FindBin::Bin/../lib";
use Acme::Frobnitz;

# Instantiate Frobnitz object for watermarking
my $frobnitz = Acme::Frobnitz->new();

# Optional metadata JSON for URL
my $metadata_arg = shift @ARGV;

my $test_url;
if ($metadata_arg) {
    my $metadata_file = -f $metadata_arg
      ? $metadata_arg
      : File::Spec->catfile($FindBin::Bin, '..', 'metadata', $metadata_arg);

    open my $mfh, '<', $metadata_file or die "Cannot open $metadata_file: $!";
    my $meta_json = do { local $/; <$mfh> };
    close $mfh;
    my $meta = decode_json($meta_json);
    $test_url = $meta->{url} or die "No URL in $metadata_file";
} else {
    my $config_file =
      File::Spec->catfile($FindBin::Bin, '..', 'conf', 'app_config.json');
    open my $cfg_fh, '<', $config_file or die "Cannot open $config_file: $!";
    my $json_text = do { local $/; <$cfg_fh> };
    close $cfg_fh;
    my $config = decode_json($json_text);
    $test_url = $config->{test_url}
      // die "test_url not found in $config_file";
}

# BEGIN TESTS
$logger->info("Starting test suite for Acme::Frobnitz");

# Test that Acme::Frobnitz has the 'download' method
can_ok('Acme::Frobnitz', 'download') or do {
    $logger->error("download method not found in Acme::Frobnitz");
    BAIL_OUT("download method not found in Acme::Frobnitz");
};

$logger->info("Test URL for download: $test_url");

# Attempt to download a YouTube video and check for errors
my $output_file;

eval {
    $output_file = $frobnitz->download($test_url);
};

if ($@) {
    $logger->error("Error during download: $@");
    fail("Download method threw an exception");
} else {
    ok($output_file, "Download method completed without errors");
    $logger->info("Download method completed successfully");
}

# Download output file path
my ($downloaded_file) = (split /\n/, $output_file)[-1];
chomp($downloaded_file);

# Verify download
if ($frobnitz->verify_file($downloaded_file)) {
    pass("File verification successful");
    $logger->info("File verification successful");
} else {
    fail("File verification failed");
    $logger->error("File verification failed");
    BAIL_OUT("Verification failed, stopping test.");
}

# Add watermark to the downloaded file
$output_file = $frobnitz->add_watermark($downloaded_file);
($downloaded_file) = (split /\n/, $output_file)[-1];
chomp($downloaded_file);
ok($downloaded_file, "Watermark added: $downloaded_file");
$logger->info("Watermark added to: $downloaded_file");

done_testing();
