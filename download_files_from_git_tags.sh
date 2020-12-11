


######################
#
# RUN COMMAND:
#
# bash download_files_from_git_tags.sh [github url] [name] [releases to download] [services name pattern. use grep pattern] [aegeus parser]
#
# - Example:
# bash download_files_from_git_tags.sh https://github.com/spinnaker/igor/ spinnaker-igor 100 Controller.java java
#

git_clone_from_tag() {
	tag_name=$1
	cd "$HOMEDIR/repos/$REPOSITORY_NAME"
	git clone --depth 1 --branch $tag_name $REPOSITORY_URL "$tag_name"
}

HOMEDIR=~/.aegeus
MAIN_DIR=$PWD
FILE=.aegeus/git_tags.out
REPOSITORY_URL=$1
REPOSITORY_NAME=$2
RELEASES=$3
SERVICES_PATTERN=$4
AEGEUS_PARSER=$5 
# create aegeus path
mkdir -p $HOMEDIR

# remove previous files
rm -rf $HOMEDIR/repos/$REPOSITORY_NAME

# recreate
mkdir -p "$HOMEDIR/repos"
mkdir -p "$HOMEDIR/repos/$REPOSITORY_NAME"
mkdir -p "$HOMEDIR/repos/$REPOSITORY_NAME/master"


#### clone repo temp
cd "$HOMEDIR/repos/$REPOSITORY_NAME/master"
git clone $REPOSITORY_URL .

# create new fale
# use "| head -n <number>" to limit n last releases
tags=$(git tag --sort=-version:refname | grep -v -E "ea|rc|beta|version" | head -n $RELEASES)

echo "GETTING LAST #$RELEASES RELEASES"

for i in $tags; do git_clone_from_tag $i; done 

cd $MAIN_DIR

echo "\n==============================="
echo "RUN AEGEUS ON VESRIONS"
echo "==============================="
echo "\n\n"
bash get_implementations_and_run_aegeus.sh $REPOSITORY_NAME $SERVICES_PATTERN $AEGEUS_PARSER