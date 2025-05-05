#!/usr/bin/perl

use strict;
use warnings;
use Test::More;
use FindBin;
use lib "$FindBin::Bin/../lib";
use Acme::Frobnitz;

# ---------------------------
# Setup: Get input URL
# ---------------------------
my $test_url = $ARGV[0] or die "Usage: $0 <Instagram URL>\n";

diag("Testing URL: $test_url");

# ---------------------------
# Step 1: Create Frobnitz object
# ---------------------------
my $frobnitz = Acme::Frobnitz->new();
ok($frobnitz, "Frobnitz object created");

# ---------------------------
# Step 2: Download the video
# ---------------------------
my $downloaded_file = eval { $frobnitz->download($test_url) };
bail_out_test("Exception during download: $@") if $@;

# Clean filename from any wrapping quotes
$downloaded_file =~ s/^['"]//;
$downloaded_file =~ s/['"]$//;

# Allow time for external drives to finish writing
sleep(1);

ok($downloaded_file && -e $downloaded_file, "Downloaded file exists: $downloaded_file")
    or bail_out_test("Downloaded file missing: $downloaded_file");

diag("Downloaded file path: $downloaded_file");

# ---------------------------
# Step 3: Verify downloaded file
# ---------------------------
ok($frobnitz->verify_file($downloaded_file), "File verification successful")
    or bail_out_test("File verification failed");

# ---------------------------
# Step 4: Add watermark
# ---------------------------
my $watermarked_file = eval { $frobnitz->add_watermark($downloaded_file) };
bail_out_test("Exception during watermarking: $@") if $@;

$watermarked_file =~ s/^['"]//;
$watermarked_file =~ s/['"]$//;
sleep(1);

ok($watermarked_file && -e $watermarked_file, "Watermarked file exists: $watermarked_file")
    or bail_out_test("Watermarked file missing: $watermarked_file");

diag("Watermarked file path: $watermarked_file");

# ---------------------------
# Step 5: Add basic captions
# ---------------------------
my $captioned_file = eval { $frobnitz->add_basic_captions($watermarked_file) };
bail_out_test("Exception during adding captions: $@") if $@;

$captioned_file =~ s/^['"]//;
$captioned_file =~ s/['"]$//;
sleep(1);

ok($captioned_file && -e $captioned_file, "Captioned file exists: $captioned_file")
    or bail_out_test("Captioned file missing: $captioned_file");

diag("Captioned file path: $captioned_file");

# ---------------------------
# Done
# ---------------------------
done_testing();

# ---------------------------
# Helper: Fatal bail out
# ---------------------------
sub bail_out_test {
    my ($message) = @_;
    diag("FATAL ERROR: $message");
    BAIL_OUT($message);
}
