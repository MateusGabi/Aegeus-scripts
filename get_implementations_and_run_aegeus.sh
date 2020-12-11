get_impl() {
	directory=$1
	cd $REPOSITORY_DIR/$directory
	
	# essa query tem que ser por cada projeto
	# sitewhere use: find "$(pwd)" | grep Impl
	files=$(find "$(pwd)" | grep Controller.java)
	for i in $files; do
		echo ">> Service: $i"
		echo ">> VERSION: $1"
		echo "$i" >> "$REPOSITORY_ANALYSIS_DIR/SERVICES.out"
		java -jar $JAR -f $i -p java -v $directory >> "$REPOSITORY_ANALYSIS_DIR/final.csv"
	done
}

MAIN_DIR=$PWD
AEGEUS_HOMEDIR=~/.aegeus
REPOSITORY_NAME=$1
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