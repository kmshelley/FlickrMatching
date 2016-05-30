# MapReduce photo comparison

Runs the photo cross comparisons as a Hadoop streaming job with an input TXT file of all pairs of photos (modified vs. original). Requires both sets of photos to be available as JAR archives `original.jar` and `modified.jar`. The JAR files are not available in this repo due to size restrictions.

First, clone this repo. Then unzip and move the TXT file `to_process.txt` to HDFS with the following commands:

```
cd FlickrMatching
tar xzf ./mapreduce/to_process.txt.zip
cd /usr/local/hadoop
hadoop fs -put ~/FlickrMatching/mapreduce/to_process.txt /input/.
```

The Hadoop streaming job can then be called with the following command:

```
hadoop jar $(ls $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar) \
	-archives ~/FlickrMatching/mapreduce/modified.jar,~/FlickrMatching/mapreduce/original.jar \
	-D stream.non.zero.exit.is.failure=false \
	-files ~/FlickrMatching/mapreduce/FlickrMatching_Map.py,~/FlickrMatching/mapreduce/FlickrMatching_Red.py \
    -mapper FlickrMatching_Map.py \
	-reduer FlickrMatching_Red.py \
    -input /input \
    -output /output
```
