#!/usr/bin/perl

use strict;
use warnings;
use Test::More;
use File::Spec;
use FindBin;
use Cwd 'abs_path';
use Log::Log4perl;
use File::Path 'make_path';

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

# Initialize Log4perl
my $log_config = qq(
log4perl.logger                    = INFO, FileAppender

log4perl.appender.FileAppender     = Log::Log4perl::Appender::File
log4perl.appender.FileAppender.filename = $log_file
log4perl.appender.FileAppender.layout   = Log::Log4perl::Layout::PatternLayout
log4perl.appender.FileAppender.layout.ConversionPattern = %d [%p] %m%n
);
Log::Log4perl->init(\$log_config);

# Create logger
my $logger = Log::Log4perl->get_logger();

# Adding the library path relative to this test script
use lib "$FindBin::Bin/../lib";
use Acme::Frobnitz;

# URL to test the download functionality
my $test_url = 'https://www.youtube.com/watch?v=DAjMZ6fCPOo';

# BEGIN TESTS
$logger->info("Starting test suite for Acme::Frobnitz");

# Ensure the module has the download method
can_ok('Acme::Frobnitz', 'download') or do {
    $logger->error("download method not found in Acme::Frobnitz");
    BAIL_OUT("download method not found in Acme::Frobnitz");
};

$logger->info("Test URL for download: $test_url");

# Attempt to download a YouTube video
my $output_file;

eval {
    $output_file = Acme::Frobnitz->download($test_url);
};

if ($@) {
    $logger->error("Error during download: $@");
    fail("Download method threw an exception");
} else {
    ok($output_file, "Download method completed without errors");
    $logger->info("Download method completed successfully");

    # Verify the output file has the expected `.webm` extension
    if ($output_file =~ /\.webm$/) {
        pass("Output file has the expected .webm extension");
        $logger->info("Output file has the expected .webm extension: $output_file");
    } else {
        fail("Output file does not have the expected .webm extension");
        $logger->error("Output file does not have the expected .webm extension: $output_file");
    }
}

done_testing();

