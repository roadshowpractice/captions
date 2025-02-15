use strict;
use warnings;
use Acme::Frobnitz;

# Instantiate the Frobnitz object
my $frobnitz = Acme::Frobnitz->new();

# URL of the video to download
my $video_url = "https://www.instagram.com/p/DFy5m4MotA5/";

# Step 1: Download the video
print "Starting download for URL: $video_url\n";
my $download_output = $frobnitz->download($video_url);

# Extract the last line of the output
my @output_lines = split(/\n/, $download_output);  # Split output into lines
my $last_line = $output_lines[-1];                # Get the last line

# Chomp the last line to clean it up
chomp($last_line);

print "HEY: $last_line\n";
print "Downloaded video to: $last_line\n";

# Step 2: Verify the downloaded file
print "Verifying downloaded file...\n";
if ($frobnitz->verify_file($last_line)) {
    print "File verification successful.\n";
} else {
    die "File verification failed. Aborting further processing.\n";
}

# Step 3: Add watermark to the downloaded video
print "Adding watermark to: $last_line\n";
$download_output = $frobnitz->add_watermark($last_line);

# Extract the last line of the output
@output_lines = split(/\n/, $download_output);  # Split output into lines
$last_line = $output_lines[-1];                # Get the last line

# Chomp the last line to clean it up
chomp($last_line);

print "HEY: $last_line\n";


# Step 2: Verify the downloaded file
print "Verifying downloaded file...\n";
if ($frobnitz->verify_file($last_line)) {
    print "File verification successful.\n";
} else {
    die "File verification failed. Aborting further processing.\n";
}

#my $image_dir = '/Users/mymac/Desktop/2024-12-22/post';
#print "Image dir is $image_dir\n";
$download_output = $frobnitz->add_basic_captions($last_line);

# Extract the last line of the output
@output_lines = split(/\n/, $download_output);  # Split output into lines
$last_line = $output_lines[-1];                # Get the last line

# Chomp the last line to clean it up
chomp($last_line);

print "HEY: $last_line\n";




