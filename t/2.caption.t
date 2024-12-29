#!/usr/bin/perl

use strict;
use warnings;
use Test::More;
use File::Spec;
use FindBin;
use Cwd 'abs_path';
use Log::Log4perl;
use File::Path 'make_path';
use IPC::System::Simple qw(capturex);

# Set log directory and file
my $log_dir = File::Spec->catdir($FindBin::Bin, '..', 'log');
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

# Paths for testing
my $video_path = '/media/fritz/E4B0-3FC2/2024-12-21/Tim_Ballard_20241211_watermarked.mp4';
my $caption_script = '/home/fritz/Desktop/frobnitz-main/bin/call_captions.py';

# Test: Captioning with existing file
subtest 'Captioning with existing file' => sub {
    ok(-e $video_path, 'Video file exists');    # Ensure the file exists

    my ($stdout, $stderr);
    eval {
        ($stdout, $stderr) = capturex('python3', $caption_script, $video_path);
    };

    if ($@) {
        $logger->error("Captioning script failed with error: $@");
        fail('Captioning script runs without error');
    } else {
        $logger->info("Captioning script output:\n$stdout");
        $logger->error("Captioning script error output:\n$stderr") if $stderr;
        pass('Captioning script runs without error');
    }
};

# Done testing
done_testing();

