

######################
#
# RUN COMMAND:
#
# bash get_implementations_and_run_aegeus.sh [project] [services name pattern. use grep pattern] [aegeus parser]
#
#

get_impl() {
	directory=$1
	cd $REPOSITORY_DIR/$directory
	
	# essa query tem que ser por cada projeto
	# sitewhere use: find "$(pwd)" | grep Impl
	# others: $(find "$(pwd)" | grep Controller.java)
	files=$(find "$(pwd)" | grep $PATTERN_SERVICES)
	for i in $files; do
		echo ">> Service: $i"
		echo ">> VERSION: $1"
		echo "$i" >> "$REPOSITORY_ANALYSIS_DIR/SERVICES.out"
		java -jar $JAR -f $i -p $AEGEUS_PARSER -v $directory >> "$REPOSITORY_ANALYSIS_DIR/final.csv"
	done
}

MAIN_DIR=$PWD
AEGEUS_HOMEDIR=~/.aegeus
REPOSITORY_NAME=$1
PATTERN_SERVICES=$2
AEGEUS_PARSER=$3
REPOSITORY_DIR=$AEGEUS_HOMEDIR/repos/$REPOSITORY_NAME
REPOSITORY_ANALYSIS_DIR=$REPOSITORY_DIR/analysis
JAR=/home/mgm/Documents/Unicamp/Aegeus/target/Aegeus-1.0-SNAPSHOT-jar-with-dependencies.jar

mkdir -p $REPOSITORY_ANALYSIS_DIR
rm -rf $REPOSITORY_ANALYSIS_DIR
mkdir -p $REPOSITORY_ANALYSIS_DIR

mkdir -p $REPOSITORY_ANALYSIS_DIR/images

echo "on $PWD"

echo "REPOSITORY set $REPOSITORY_NAME"

cd $REPOSITORY_DIR

### paths ordered by semver
### see: https://stackoverflow.com/questions/40390957/how-to-sort-semantic-versions-in-bash
paths=$(ls)
for dir in $paths; do get_impl $dir; done

cd $MAIN_DIR
python3 get_unique_services.py $REPOSITORY_ANALYSIS_DIR/SERVICES.out $REPOSITORY_ANALYSIS_DIR/final.csv $REPOSITORY_ANALYSIS_DIR