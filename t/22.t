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
make_path($log_dir) unless -d $log_dir;

my $log_config = qq(
log4perl.logger = INFO, FileAppender
log4perl.appender.FileAppender = Log::Log4perl::Appender::File
log4perl.appender.FileAppender.filename = $log_file
log4perl.appender.FileAppender.layout = Log::Log4perl::Layout::PatternLayout
log4perl.appender.FileAppender.layout.ConversionPattern = %d [%p] %m%n
);
Log::Log4perl->init(\$log_config);
my $logger = Log::Log4perl->get_logger();

# Add library path
use lib "$FindBin::Bin/../lib";
use Acme::Frobnitz;

# Ensure a URL is provided as an argument
if (@ARGV < 1) {
    $logger->fatal("No URL provided. Usage: $0 <video_url>");
    die "Usage: $0 <video_url>\n";
}

# Get the test URL from command line arguments
my $test_url = $ARGV[0];
$logger->info("Starting test suite for Acme::Frobnitz");
$logger->info("Test URL for download: $test_url");

# Create Frobnitz object
my $frobnitz = Acme::Frobnitz->new();

# Test that Acme::Frobnitz has the 'download' method
can_ok('Acme::Frobnitz', 'download') or bail_out_with_log("download method not found in Acme::Frobnitz");

# Download the video
my $output_file = handle_download($frobnitz, $test_url);
$logger->info("Downloaded file: $output_file");

# Verify download
verify_file($frobnitz, $output_file);
$logger->info("Verified file: $output_file");

# Add watermark to the downloaded file
my $watermarked_file = handle_watermark($frobnitz, $output_file);
$logger->info("Watermarked file: $watermarked_file");

# Add clips using the correct watermarked filename
handle_clips($frobnitz, $watermarked_file);
$logger->info("Clips created from: $watermarked_file");

done_testing();
$logger->info("Test suite completed successfully");

# ----------------- Helper Subroutines -----------------

# Subroutine to handle download and error checking
sub handle_download {
    my ($frobnitz, $url) = @_;
    my $output_file;
    
    eval {
        $output_file = $frobnitz->download($url);
    };
    if ($@) {
        $logger->error("Error during download: $@");
        fail("Download method threw an exception");
        return;
    }
    
    ok($output_file, "Download method completed without errors");
    $logger->info("Download method completed successfully");

    if (!$output_file) {
        $logger->fatal("No file was downloaded.");
        fail("Download failed");
        return;
    }

    $logger->info("Downloaded file: $output_file");

    my ($file_path) = (split /\n/, $output_file)[-1]; # Extract the file path
    chomp($file_path);
    
    if (!$file_path || !-e $file_path) {
        $logger->fatal("Downloaded file path is invalid or does not exist: $file_path");
        fail("Downloaded file path is invalid");
        return;
    }
    
    return $file_path;
}

# Subroutine to verify downloaded file
sub verify_file {
    my ($frobnitz, $file) = @_;
    
    if ($frobnitz->verify_file($file)) {
        pass("File verification successful");
        $logger->info("File verification successful: $file");
    } else {
        fail("File verification failed");
        $logger->error("File verification failed: $file");
        bail_out_with_log("Verification failed, stopping test.");
    }
}

# Subroutine to handle watermarking
sub handle_watermark {
    my ($frobnitz, $file) = @_;
    
    my $watermarked_file = $frobnitz->add_watermark($file);
    chomp($watermarked_file);

    if (!$watermarked_file || !-e $watermarked_file) {
        $logger->error("Failed to add watermark to file: $file");
        fail("Watermark addition failed");
        return;
    }

    ok($watermarked_file, "Watermark added: $watermarked_file");
    $logger->info("Watermark added to: $watermarked_file");

    return $watermarked_file; # Return new file path
}

# Subroutine to handle clips creation
sub handle_clips {
    my ($frobnitz, $file) = @_;
    
    my $clip_file = $frobnitz->add_clipped_captions($file);
    
    if (!$clip_file || !-e $clip_file) {
        $logger->error("Failed to add clips to file: $file");
        fail("Clip addition failed");
        return;
    }

    chomp($clip_file);

    ok($clip_file, "Clips added: $clip_file");
    $logger->info("Clips added to: $clip_file");
}

# Helper subroutine for logging and bailing out
sub bail_out_with_log {
    my ($message) = @_;
    $logger->fatal($message);
    BAIL_OUT($message);
}
