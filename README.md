![Python package](https://github.com/AzemaBaptiste/topper/workflows/Python%20package/badge.svg)

<img src="https://upload.wikimedia.org/wikipedia/commons/7/7a/Emojione_1F3A9.svg" height="80" />

Topper 
===========

Topper is a library made to parse and process log files of music
listening. The purpose of this application
is to get the top 50 songs the most listened on the
last 7 days grouped by country or user id.

You must provide:
- landing_folder: where daily files are sent
- checkpoint_directory: used by the application to process, archive and 
persist data across days
- output_directory: where result files are written everyday
- mode (optional): `country` (default) or `user` is the aggregation mode

## Input files
Each log file must match the pattern
listen-YYYYMMDD.log. 
The file must contains data structured with:
- One row per stream (1 listening).
- Each row is in the following format: `song_id|user_id|country`

#### File management
Input files will be moved to the directory `checkpoint/current/`

Invalid files will be moved to the directory `checkpoint/errors/`

Data files older than 7 days will be moved to the directory `checkpoint/archive/`


## Output files

### Mode 'country'
Produced files have the following format: 

    country1|sng_id1:n1,sng_id2:n2,sng_id3:n3,...,sng_id50:n50
    country2|sng_id1:n1,sng_id2:n2,sng_id3:n3,...,sng_id50:n50
    
Where country is the country ISO2 code, sng_id1:n1 the identifier of the song the most 
listened with the related number of streams, sng_id2:n2 the identifier of the 2nd song
 the most listened with the related number of streams and so on..
 
### Mode 'user'
Produced files have the following format: 

    user_id1|sng_id1:n1,sng_id2:n2,sng_id3:n3,...,sng_id50:n50
    user_id2|sng_id1:n1,sng_id2:n2,sng_id3:n3,...,sng_id50:n50
    
Where user_id is a user, sng_id1:n1 the identifier of the song the most 
listened with the related number of streams, sng_id2:n2 the identifier of the 2nd song
 the most listened with the related number of streams and so on..


## Usage

#### Supported Python Versions
Python >= 3.6

#### Installation

    virtualenv -p python3 venv
    source venv/bin/activate
    make install

Display usage
    
    topper -h
    
#### Example

    topper --landing_folder sample/ --checkpoint_directory checkpoint --output_directory output --mode country

#### Development
    
    make test # coverage tests
    make linter # runs pylint
    make build
