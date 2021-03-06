import os


# Download lake_metadata.csv
# This is a checkpoint because lake_metadata.csv is needed to determine 
# later outputs; namely, the lake_sequence file names.
checkpoint fetch_mntoha_metadata:
    input:
        "1_fetch/in/pull_date.txt",
    output:
        "1_fetch/out/lake_metadata.csv"
    params:
        sb_id = "5e5c1c1ce4b01d50924f27e7"
    script:
        "1_fetch/src/sb_fetch.py"


# Download MNTOHA temperature observations zip file
rule fetch_mntoha_obs:
    input:
        "1_fetch/in/pull_date.txt"
    output:
        "1_fetch/tmp/obs_mntoha/temperature_observations.zip"
    params:
        sb_id = "5e5d0b68e4b01d50924f2b32"
    script:
        "1_fetch/src/sb_fetch.py"


# Download MNTOHA meteorological drivers, clarity, and ice flag zip files
rule fetch_mntoha_dynamic:
    input:
        "1_fetch/in/pull_date.txt"
    output:
        "1_fetch/tmp/dynamic_mntoha/{file}"
    params:
        sb_id = "5e5d0b96e4b01d50924f2b34"
    script:
        "1_fetch/src/sb_fetch.py"


# Download metadata for lakes across CONUS compiled by Willard et al., 2022:
# Publication: https://doi.org/10.1002/lol2.10249
rule fetch_surface_metadata:
    input:
        "1_fetch/in/pull_date.txt",
    output:
        "1_fetch/out/surface/lake_metadata.csv"
    params:
        sb_id = "60341c3ed34eb12031172aa6"
    script:
        "1_fetch/src/sb_fetch.py"


# Unzip files from a zipped archive.
#
# This is a checkpoint because otherwise Snakemake won't track unzipped files
# from an archive and will delete or ignore them. The output is a directory
# because we don't know how many unzipped files there will be, but we know
# which directory they'll be in after they are unzipped.
checkpoint unzip_archive:
    input:
        "1_fetch/tmp/{file_category}/{archive_name}.zip"
    output:
        # The output is the name of the directory that files are extracted to.
        # Regular expressions ensure that files in subdirectories of
        # 1_fetch/out/{file_category} don't get matched, and csvs in
        # 1_fetch/out/ don't get matched.
        # 
        # Regular expression syntax explanation:
        # snakemake allows regular expressions to match wildcards by placing
        # them after a comma, like this: {wildcard,regex}
        # [^/] means any character that is not / (so, not a subdirectory), and
        # + means one or more of the previous
        # So, [^/]+ means match any string that doesn't have a / in it.
        # $ means to the end of the string, and (?<!string) is a negative lookbehind
        # So, $(?<!\.csv) means don't match if the final characters in the string are .csv
        folder = directory("1_fetch/out/{file_category,[^/]+}/{archive_name,[^/]+$(?<!\.csv)}")
    params:
        source_dir = "1_fetch/tmp",
        destination_dir = "1_fetch/out"
    script:
        "1_fetch/src/unzip_file.py"


