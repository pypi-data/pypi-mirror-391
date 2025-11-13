[![Hits](https://hits.sh/github.com/abdallahheidar/tweetcaptureplus.svg?label=TweetCapturePlus%20Views&extraCount=142)](https://hits.sh/github.com/abdallahheidar/tweetcaptureplus/)

# TweetCapturePlus

Easily take screenshots of **tweets**, **mentions**, and **full threads**.

# About This Fork

This project is a fork of xacnio/tweetcapture. It includes the following additional functionality.

**What's new**

- Take screenshots of long Tweets (that require scrolling to capture)
- Some settings are default now: overwrite, Dim mode, Capture full threads

**Bug fixes**

- Fixed an issue where the screenshot would be cut off when the tweet was too long
- Fixed issues related to the Twitter UI changes

**Deprecated Features**

- Scale, Mode

The original project is licensed under the MIT License, and this fork retains the same license.

## Command-Line Usage

```
> pip install tweetcaptureplus
> tweetcaptureplus https://x.com/elonmusk/status/1519480761749016577
> tweetcaptureplus -h
```

## Code Usage Examples

- [CLI](tweetcaptureplus/cli.py)
- [Code Examples](tweetcaptureplus/examples/)

## Testing

```
> pip install opencv-python numpy
> cd tweetcaptureplus/tests/
> python -m unittest
```

## Docker Usage

```
docker run --rm -v $(pwd):/app xacnio/tweetcaptureplus -h
docker run --rm -v $(pwd):/app xacnio/tweetcaptureplus https://x.com/elonmusk/status/1519480761749016577
```

- _<font size="1">On Windows: Replace `$(pwd)` with `${PWD}`_ (**Powershell**)
- _On Windows: Replace `$(pwd)` with `%cd%`_ (**Command Line**)</font>

## Night Modes

| #   | Night Mode | Screenshot                                                                 |
| --- | ---------- | -------------------------------------------------------------------------- |
| 0   | Default    | <img src="/tweetcaptureplus/assets/night_mode_default.png" width="500">    |
| 1   | Dim        | <img src="/tweetcaptureplus/assets/night_mode_dim.png" width="500">        |
| 2   | Lights out | <img src="/tweetcaptureplus/assets/night_mode_lights_out.png" width="500"> |

## Show Mentions Example

_If the tweet have a very many mentions, there may be problems because "show more" option not supported. The tool can show only first loaded mentions. You can limit mention count on screenshot by using -sc <count> argument_

```
tweetcaptureplus -sm 3 https://twitter.com/Twitter/status/1445078208190291973
```

<img src="https://i.imgur.com/IZ0GHl8.png" />

## Show Parent Tweets Example

**NOTICE:** You have to be logged in the show the full thread.

```
tweetcaptureplus -sp https://x.com/elonmusk/status/1746970616060580326
```

<img src="/tweetcaptureplus/assets/@elonmusk_1746970616060580326.png" width="500">
