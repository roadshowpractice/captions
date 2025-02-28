use strict;
use warnings;
use File::Path qw(make_path);

# Define the input file and the output directory
my $input_file = '/Volumes/BallardT1/2025-02-24/Wars.txt';
my $output_dir = '/Volumes/BallardT1/2025-02-24/wars';

# Create the output directory if it doesn't exist
make_path($output_dir) unless -d $output_dir;

# Mapping Roman numerals to Arabic numbers
my %roman_to_arabic = (
    'I'  => 1,
    'II' => 2,
    'III' => 3,
    'IV' => 4,
    'V'  => 5,
    'VI' => 6,
    'VII' => 7,
    'VIII' => 8,
    'IX' => 9,
    'X' => 10,
    'XI' => 11,
    'XII' => 12,
    'XIII' => 13,
    'XIV' => 14,
    'XV' => 15,
    'XVI' => 16,
    'XVII' => 17,
    'XVIII' => 18,
    'XIX' => 19,
    'XX' => 20,
    'XXI' => 21,
    'XXII' => 22,
    'XXIII' => 23,
    'XXIV' => 24,
    'XXV' => 25,
    'XXVI' => 26,
    'XXVII' => 27,
    'XXVIII' => 28,
    'XXIX' => 29,
    'XXX' => 30,
);

# Open the input file for reading
open my $fh, '<', $input_file or die "Cannot open file $input_file: $!";

# Initialize variables
my $book_number = 1;
my $book_content = '';
my $in_book = 0;

while (my $line = <$fh>) {
    chomp $line;

    # Detect the start of a new book (by matching "BOOK" followed by Roman numerals)
    if ($line =~ /^BOOK\s+(\w+)/) {
        my $roman_numeral = $1;

        # If the Roman numeral matches one in our mapping, assign the book number
        if (exists $roman_to_arabic{$roman_numeral}) {
            # Save the previous book if it exists
            if ($in_book) {
                save_book($book_number, $book_content);
                $book_number++;
            }

            # Set the book number based on the Roman numeral
            $book_number = $roman_to_arabic{$roman_numeral};

            # Start new book content
            $book_content = "$line\n";
            $in_book = 1;
        }
    } else {
        # Accumulate content for the current book
        $book_content .= "$line\n" if $in_book;
    }
}

# Save the last book if any
save_book($book_number, $book_content) if $in_book;

# Close the input file
close $fh;

# Function to save a book to a separate file
sub save_book {
    my ($book_number, $content) = @_;
    my $book_filename = "$output_dir/book_$book_number.txt";
    
    open my $out_fh, '>', $book_filename or die "Cannot write to $book_filename: $!";
    print $out_fh $content;
    close $out_fh;
    print "Saved: $book_filename\n";
}
