use strict;
use warnings;
use File::Path qw(make_path);

# Define the input directory containing the books and the output file
my $input_dir = '/Volumes/BallardT1/2025-02-24/books';
my $output_file = '/Volumes/BallardT1/2025-02-24/came_to_pass_output.txt';

# Open the output file for writing
open my $out_fh, '>', $output_file or die "Cannot open output file $output_file: $!";

# Function to get the book number from the filename (extracting the number after the underscore)
sub get_book_number {
    my ($filename) = @_;
    
    # Verbose logging
    print "Checking filename: $filename\n";
    
    if ($filename =~ /book_(\d+)/) {
        my $book_number = $1;
        print "Found book number: $book_number\n";  # Verbose logging
        return $book_number;  # Return the number after the underscore
    } else {
        print "Book number not found for filename: $filename\n";  # Verbose logging
        return "unknown";  # Return 'unknown' if the number is not found
    }
}

# Process each file in the books directory
opendir my $dir, $input_dir or die "Cannot open directory $input_dir: $!";

print "Reading directory: $input_dir\n";

while (my $file = readdir($dir)) {
    next if $file =~ /^\./;  # Skip hidden files (e.g., .DS_Store)

    my $file_path = "$input_dir/$file";
    print "Processing file: $file_path\n";  # Verbose logging
    
    my $book_number = get_book_number($file);
    print "Book number for $file: $book_number\n";  # Verbose logging

    # Open the current book file for reading
    open my $fh, '<', $file_path or die "Cannot open file $file_path: $!";

    my $line_number = 1;  # Track the line number
    my $matches_found = 0;  # Flag to track if matches are found

    while (my $line = <$fh>) {
        chomp $line;

        # Check for the phrase "came to pass"
        if ($line =~ /came to pass.*?[.!?]/) {
            print $out_fh "File: $file, Book $book_number, Line $line_number: $line\n";
            print "Match found: File: $file, Book $book_number, Line $line_number: $line\n";  # Verbose logging
            $matches_found = 1;
        }

        $line_number++;
    }

    # Verbose logging if no matches were found in this file
    if (!$matches_found) {
        print "No matches found in file: $file\n";
    }

    close $fh;
}

closedir $dir;
close $out_fh;

print "Done processing all books.\n";
