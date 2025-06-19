#!/usr/bin/perl

use strict;
use warnings;
use Test::More;
use FindBin;
use File::Spec;
use JSON qw(decode_json encode_json);
use lib "$FindBin::Bin/../lib";
use Acme::Frobnitz;

# ---------------------------
# Setup: Get metadata file and URL
# ---------------------------
my $metadata_arg = shift @ARGV
  or die "Usage: $0 <metadata.json>\n";

# If a relative path is given, assume it is in the metadata directory
my $metadata_file = -f $metadata_arg
  ? $metadata_arg
  : File::Spec->catfile( $FindBin::Bin, '..', 'metadata', $metadata_arg );

open my $mfh, '<', $metadata_file
  or die "Cannot open $metadata_file: $!";
my $json_text = do { local $/; <$mfh> };
close $mfh;

my $meta     = decode_json($json_text);
my $test_url = $meta->{url}
  or die "No URL field in $metadata_file\n";

diag("Testing URL from $metadata_file: $test_url");

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
$meta->{tasks}{perform_download} = $downloaded_file;

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
$meta->{tasks}{apply_watermark} = $watermarked_file;

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
$meta->{tasks}{add_captions} = $captioned_file;

diag("Captioned file path: $captioned_file");

# ---------------------------
# Update metadata with results
# ---------------------------
open my $out, '>', $metadata_file
  or die "Cannot write $metadata_file: $!";
print $out encode_json($meta);
close $out;

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
