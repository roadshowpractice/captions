use 5.006;
use strict;
use warnings;
use ExtUtils::MakeMaker;

WriteMakefile(
    NAME             => 'Acme::Frobnitz',
    AUTHOR           => q{Perl Gonzales <perlgonzales72@gmail.com>},
    VERSION_FROM     => 'lib/Acme/Frobnitz.pm',
    ABSTRACT_FROM    => 'lib/Acme/Frobnitz.pm',
    LICENSE          => 'artistic_2',
    MIN_PERL_VERSION => '5.006',
    CONFIGURE_REQUIRES => {
        'ExtUtils::MakeMaker' => '6.64',
    },
    TEST_REQUIRES => {
        'Test::More' => '0.88',
    },
    dist  => { COMPRESS => 'gzip -9f', SUFFIX => 'gz' },
    clean => { FILES => 'Acme-Frobnitz-*   ignore.txt' },
    PREREQ_PM => {
        # Add required modules here, e.g., 'Some::Module' => '1.23',
    },
);

__END__

