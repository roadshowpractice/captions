#!/usr/bin/perl

use strict;
use warnings;
use Test::More;
use FindBin;
use lib "$FindBin::Bin/../lib";
use Acme::Frobnitz;

# ---------------------------------------------
# Setup: Get input URL
# ---------------------------------------------
my $test_url = $ARGV[0] or die "Usage: $0 <Instagram URL>\n";

diag("Testing with URL: $test_url");

# ---------------------------------------------
# Step 1: Create Frobnitz object
# ---------------------------------------------
my $frobnitz = Acme::Frobnitz->new();
ok($frobnitz, "Frobnitz object created");

# ---------------------------------------------
# Step 2: Download the video
# ---------------------------------------------
my $downloaded_file = eval { $frobnitz->download($test_url) };
ok($downloaded_file && -e $downloaded_file, "Downloaded file exists: $downloaded_file") 
    or bail_out_test("Download failed: $@");

diag("Downloaded to: $downloaded_file");

# ---------------------------------------------
# Step 3: Verify the downloaded file
# ---------------------------------------------
ok($frobnitz->verify_file($downloaded_file), "File verification successful")
    or bail_out_test("File verification failed");

# ---------------------------------------------
# Step 4: Add watermark
# ---------------------------------------------
my $watermarked_file = eval { $frobnitz->add_watermark($downloaded_file) };
ok($watermarked_file && -e $watermarked_file, "Watermarked file exists: $watermarked_file")
    or bail_out_test("Watermarking failed: $@");

diag("Watermarked to: $watermarked_file");

# ---------------------------------------------
# Step 5: Add basic captions
# ---------------------------------------------
my $captioned_file = eval { $frobnitz->add_basic_captions($watermarked_file) };
ok($captioned_file && -e $captioned_file, "Captioned file exists: $captioned_file")
    or bail_out_test("Captioning failed: $@");

diag("Captioned to: $captioned_file");

done_testing();

# ---------------------------------------------
# Helper Subroutine
# ---------------------------------------------
sub bail_out_test {
    my ($message) = @_;
    diag("FATAL: $message");
    BAIL_OUT($message);
}
