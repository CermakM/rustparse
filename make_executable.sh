#!/usr/bin/bash

# Bash script for creating executable from rustparse.py file
# Note that the file name must not be changed in order for this script to work

SHORT=f
LONG=force
PARSED=$(getopt --options $SHORT --longoptions $LONG --name "$0" -- "$@")

eval set -- "$PARSED"

if [ ! -f ./rustparse.py ]; then
	echo "File \`rustparse.py\` was not found in current directory." >&2
	exit 1
fi

case "$1" in
	-f|--force)
		FORCE=true
esac

if [ -f ./rustparse ]; then
	if [ $FORCE ]; then :
	elif [ ! -x ./rustparse ]; then
		echo -e "Warning: File \`rustparse\` already exists in current directory but is not executable.\nUse \$chmod +x rustparse to make it executable or run with --force to overwrite" >&2
		exit 2
	else echo "Warning: File \`rustparse\` already exists in current directory, run with --force to overwrite" >&2
		fi
fi

cat > rustparse <<-'EOF'
#!/usr/bin/env python3

EOF

cat rustparse.py >> rustparse

chmod +x rustparse

exit 0
