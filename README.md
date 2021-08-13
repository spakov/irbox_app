# IR Box App
A Python web app to control devices over Wi-Fi with infrared commands using [IR box](https://github.com/spakov/irbox).

## Overview
The IR box app is a Python WSGI app that presents a web-based interface to [IR
box](https://github.com/spakov/irbox), allowing you to control devices with
infrared commands over Wi-Fi.

The app allows you to configure multiple remotes, simulating an existing remote
control, or designing your own custom ones.

The app works well in modern browsers, including on mobile platforms.

## Prerequisites
- An Arduino running [IR box](https://github.com/spakov/irbox)
- Python 3.6-ish or newer
- Flask
- A WSGI server

## Getting Started
Pull down the IR box app and point your WSGI server to `app`, being sure to
have `IRBOX_CONFIG` point to your configuration file.

If you'd like an "app" button on your iPhone's home screen, navigate to the
site in Safari, select the Share button, scroll down a bit, and select Add to
Home Screen. It creates a nice app-like button for you that opens the site in a
full-screen app-like mode.

I'd be very surprised if Android didn't have a similar feature, but I don't
have an Android device, so I cannot confirm or tell you how to do that.

## Configuration
You'll want to create a configuration file and make sure the `IRBOX_CONFIG`
environment variable is exported to it. The variable specifies the path to the
configuration file. The configuration file should be located outside the web
app directory.

The configuration file is a simple .cfg file, including the following
directives. Comments begin with `#`.

### `HOST_ADDRESS`
String. The IP address (or hostname, if you have DNS set up) of the IR box.

### `HOST_PORT`
Integer. The TCP port of the IR box. IR box's default port is 333.

### `REMOTES`
A dictionary of remotes to configure. The dictionary is in the following format:

    {
        remote_id: remote_name[,]
        […]
    }

Keep reading for more on remotes.

### `RETRY`
Boolean. Whether or not to consider a response timeout as an indication that
the connection has been terminated. Note that, due to the "lazy" communication
approach the IR box app takes, there is no reliable indication of a hard
disconnect, so this is a reasonable option if transmission issues are
encountered routinely.

### Example Configuration File
    # IR box app configuration
    HOST_ADDRESS = '192.168.0.160'
    HOST_PORT = 333
    RETRY = False
    REMOTES = {
        'demo': 'Demo Remote'
    }

## Remotes
The IR box app uses the concept of *remotes*, which are essentially digital
remote controls. Several remotes are included to get you started, including a
simple demo remote.

## The Index Page
The IR box app's index page includes a list of remotes that are configured.
Click/tap on one to use it.

At the bottom of the page, there's a "Receive Mode" link, which allows you to
put the IR box in receive mode to read IR commands that you can integrate into
your remotes. More on that later.

## Remote Pages
Each remote page includes a few core elements:
- A link to get back to the index page
- The remote itself
- An alternate alignment button to toggle the remote's alignment (useful for
  those of us who use large phones and are not ambidextrous).

The alternate alignment button sets a cookie to remember this preference across
all remotes for one year.

## Receive Mode
Receive mode is essentially a customized remote. Its purpose is to allow users
to determine what IR commands their existing physical remotes' buttons are
sending so they can be recreated using the IR box app.

The interface is pretty simple. The `#response` `<iframe>` is always visible,
and a `#remote` is displayed with a Start button and a Stop button.

Clicking/tapping Start puts the IR box in receive mode. In this state, the IR
box app queries the IR box for a message four times per second and prints the
resulting data in the `#response` `<iframe>`.

The idea is you start receive mode, point a physical remote at the IR box,
press some buttons, and note what IR commands they generate.

Responses are formatted as JavaScript objects that can be directly copied and
pasted into your remote's script file. Mouse over them to see the raw `+tx`
responses received from the IR box.

Be sure to click/tap Stop before leaving the page.

## Building Your Own Remotes
With a clean install, you'll only see the demo remote, which is not terribly
useful unless you only want to test the IR box and turn a Sony TV on and off.

Remotes are composed of four parts:
- An HTML file (required)
- A JavaScript file (optional)
- A stylesheet (optional)
- An image (optional).

Each remote has an ID (`remote_id` in the configuration file above) and a name
(`remote_name` in the configuration file above). The remote ID is any string
that can be safely represented as a file name (probably best to stick with
`[A-Za-z0-9._-]`) and the remote name is anything you like.

The IR box app validates `remote_id` for safety. It prints a warning if it
contains unsafe characters.

### Remote HTML Files
Each remote's HTML file is a Jinja2 template and is placed in
`templates/remotes/remote_id.html`, where `remote_id` is the remote's ID. Its
content would look something like the following:

    {% extends 'remote-base.html' %}
    {% block remote_content %}
      <div>
        <iframe id="response"{% if alt_align %} class="alt-align"{% endif %}></iframe>
        <button id="response-close"{% if alt_align %} class="alt-align"{% endif %} onclick="showResponse(false);">✕</button>
      </div>
      <div id="remote"{% if alt_align %} class="alt-align"{% endif %}>
        <div id="status"{% if alt_align %} class="alt-align"{% endif %} onclick="toggleResponse();"></div>
        <legend{% if alt_align %} class="alt-align"{% endif %}>Demo Remote</legend>
        <div class="grid-cluster alt-align">
          <button type="button" onclick="nop();">A</button>
          <button type="button" onclick="invalid();">B</button>
          <button type="button" onclick="tx({'p':0x13,'a':0x1,'c':0x14,'b':0xc});">C</button>
        </div>
      </div>
    {% endblock %}

The template, as the `extends` directive implies, simply extends the
`templates/remote-base.html` page, which in turn extends `templates/base.html`.

Every remote HTML page has a few core parts:
- A `#status` container, which presents a status "LED"
- A `#response` `<iframe>`, with accompanying `#response-close` element
- A `#remote` container, which contains the visual and functional content of
  the remote itself
- Several `<button>`s within the `#remote`.

The `#response`, `#response-close`, and `#status` are not strictly required, but
they are helpful.

#### `#status`
A status "LED" that changes color based on the current command
transmission/response status. Click/tap on it to toggle visibility of the
`#response`.

#### `#response`
Each remote includes the capability to display status information. The
`#response` is an `<iframe>` that displays the status of the last command
transmitted. It is not displayed by default and can be displayed by
clicking/tapping on the `#status`.

#### `#response-close`
A button that allows the user to close the `#response` `<iframe>` when desired.
Appears at the top-right corner of the `#response`.

#### `#remote`
The main container for the remote's buttons and other content. There are
several CSS helpers available, described below.

### Remote Scripts
If `static/remotes/scripts/remote_id.js` exists, it will be automatically
included in the remote's HTML. These are useful for including `tx()` function
argument objects (more on those below) without having to have them all inline in
your HTML. They can, of course, also be used for any other JavaScript code
you'd like to include in a remote page.

### Remote CSS
Similar to JavaScript files, if `static/remotes/css/remote_id.css` exists, it
will be automatically included in the remote's HTML. This is helpful in complex
cases in which it's convenient to include CSS classes that are used multiple
times throughout the remote.

### Remote Image
Like the script and stylesheet, if `static/remotes/images/remote_id.png`
exists, it will be used as a remote preview image on the index page.

### JavaScript Functions
Let's return to design after discussing how the remotes actually do what
they're designed to do.

Each remote automatically pulls in `static/irbox.js`, which includes several
useful JavaScript functions.

#### `nop()`
Sends a `nop` command to the IR box.

#### `tx(args)`
Transmits a `tx` command to the IR box, which tells it to send out an infrared
command. It takes arguments similar to IR box's `tx` command, except broken out
as an associative-array-like JavaScript object:

    { 'p': protocol, 'a': address, 'c': command[,] ['b': bits][,] ['r': repeats] }

As with IR box, `b` (bits) is only used with the Sony protocol, and `r`
(repeats) is always optional.

The function automatically converts each of the arguments to hex if they're
provided as integers (though hex is shorter anyway, so I'm not sure why you'd
want to do that).

To use the Sony TV power command as an example, we'd be looking at this object:

    { 'p': 0x13, 'a': 0x1, 'c': 0x14, 'b': 0xc }

> **Where do these numbers come from?** Use receive mode to get these
  parameters for the desired IR command.

The `tx()` function passes the command along to the IR box app, which passes it
along to the IR box.

#### `rx()`
Sends an `rx` command to the IR box, which puts it in receive mode. Note that
there's no reason to call `rx()` from a remote, since it's easily accessible
from the Receive Mode page.

#### `norx()`
Send a `norx` command to the IR box, which exits receive mode. Like `rx()`,
there's no reason to call `norx()` from a remote.

#### `invalid()`
Sends an `invalid` command to the IR box. If you've read IR box's
documentation, you'll know that this is, in fact, an invalid command, and
therefore always receives a "bad" response. This is useful primarily for
debugging and testing.

### Remote Buttons
A remote control is useless without buttons, and the IR box app is no
exception. Each remote has several buttons, the vast majority of which call the
JavaScript `tx()` function.

The idea is to determine which command you'd like each button to transmit, then
have that button call `tx()` with the appropriate arguments.

The IR box app uses the `#status` container as a simulated LED to indicate
command and response status. When the button is clicked/tapped, `#status`
blinks yellow. When a response is received from the IR box, `#status` blinks
green if a "good" response was received or red if a "bad" response was received
(or if no response was received).

These requests and updates are accomplished under the hood using a JavaScript
`XMLHttpRequest()` call.

In the case of receive mode, it is not guaranteed that a response will ever be
received. This is because responses are routed differently in receive mode than
they are in other cases. Instead of red and green, white is used instead.

The `#status` container can be clicked/tapped to display the `#response`
`<iframe>`, which, as the name suggests, displays the response received from
the IR box, including some helpful context information.

### Jinja2 Helpers
Back to design.

You'll notice `{% if alt_align %}` and associated `{% endif %}` statements
throughout the demo remote HTML file. The IR box app exposes the `alt_align`
variable to the Jinja2 templates based on the value of the alternate alignment
cookie. This allows remotes to load with the correct alignment.

`irbox.js` sets this cookie when the alternate alignment button is
clicked/tapped, which also toggles the alignment.

The `alt-align` CSS class is used to achieve this effect.

### CSS Background Information
I put a lot of work into designing a stylesheet that gives a simple but
highly customizable appearance. Buttons have simulated shadows by default and
change their appearance when moused over (if on a system with a pointer device)
and when clicked/tapped.

All of this happens automatically when using the guidance outlined below.

Pages are also responsive based on the device's dark theme setting. On Apple
devices, at least, this means a light background during the day and a dark
background at night. There are numerous tweaks in place to adjust appearance
based on the theme.

Finally, presentation has been customized to look good in a desktop web browser
and on my phone, which is an iPhone 12 Pro Max, in any orientation. I would
guess it looks halfway reasonable on other devices as well but can't confirm.

### CSS Helpers
If you take a look at `static/style.css`, which is included in every page the
IR box app presents, you'll see many useful classes and IDs. A summary of the
helpful ones for layout is presented here.

#### CSS Variables
App-specific CSS variables are used throughout the stylesheet:
- `--remote-bg`: The remote background color
- `--remote-fg`: The remote text color
- `--legend-font-size`: The font size of the `<legend>` tag
- `--legend-fg`: The `<legend>` text color
- `--button-font-size`: The button font size
- `--button-bg`: The button background color
- `--button-fg`: The button text color
- `--button-width`: The button width
- `--button-height`: The button height
- `--button-gap`: The gap between buttons
- `--button-radius`: The corner rounding radius applied to buttons

All of these can be specified with any valid CSS units. Personally, I prefer to
size things in terms of `rem`s whenever possible.

These will make more sense as we walk through some examples.

> **Why use custom variables?** The variables are used throughout the
  stylesheet. They help to dramatically reduce repetition and help with lots of
  dimensional calculations.

#### `#remote`
This style is applied to the `#remote` container. This is, generally speaking,
the first thing you want in a remote. It is not necessary to specify any
variables or properties as part of the `#remote`, but in doing so, great
customization can be achieved.

As a more complex example, something like the following could be used:

    <div id="remote"{% if alt_align %} class="alt-align"{% endif %} style="--legend-font-size: 9pt; --legend-fg: white; --remote-bg: #333; --remote-fg: white; --button-bg: #666; --button-fg: white; --button-width: 2rem; --button-height: 2rem; --button-gap: 0.4rem; --button-radius: 0.5ex; --button-font-size: 11pt; max-width: calc(var(--button-width) * 5 + var(--button-gap) * 6); border-radius: 0.5rem 0.5rem 1rem 1rem;">

Let's break it down into parts.

##### `alt_align`/`.alt-align`
If alternate alignment (`alt_align`) is enabled, include the `alt-align` class
by default.

##### `--legend-font-size`
In some cases, it's helpful to use the HTML `<legend>` tag to label buttons or
portions of the remote. `<legend>` is really designed to be used inside
`<fieldset>` (though it doesn't have to be), which is helpful to group controls
or emulate the style of an existing physical remote.

In other cases, it's easier to use a `<span>`.

In any case, this example sets the `<legend>` font size to 9 point.

##### `--legend-fg`
Sets the `<legend>` text color to white.

##### `--remote-bg`
Sets the remote's background color to dark gray.

##### `--button-bg`
Gives buttons a slightly lighter gray color than the remote.

##### `--button-fg`
Sets the button text color to white.

##### `--button-width`
Sets the width of buttons to 2 `rem`.

> **Why `rem` instead of `em`?** `rem`s (root `em`s, presumably) are helpful to
  keep consistent dimensions regardless of the font size within a particular
  element. For example, 1 `em` at 8 point is much tinier than 1 `em` at 16
  point. `rem`s normalize to the root element's (that is, `<html>`'s) font
  size, regardless of a particular element's font size.

##### `--button-height`
Sets the height of buttons to 2 `rem`. (Square buttons, in this case.)

##### `--button-gap`
Configures a gap of 0.5 `rem` between buttons.

##### `--button-radius`
Gives buttons a slightly rounded appearance with a radius of 0.5 `ex`.

##### `--button-font-size`
Sets button text size to 11 point.

##### `max-width`
Calculate the `#remote`'s maximum (and, for all intents and purposes, actual)
width. This is important because it's based on the nominal number of buttons in
a row. In this example, we're setting this to `calc(var(--button-width) * 5 +
var(--button-gap) * 6)`. Since buttons have a gap on either side, we're saying
we want the remote to have room for five buttons and five plus one gaps.

#### `border-radius`
In this case, the remote has a rounded appearance, with slightly less rounded
top corners (0.5 `rem`) than the bottom corners (1 `rem`).

#### `#status`
The first element in the `#remote` should be the `#status`. This is pretty
straightforward:

    <div id="status" onclick="toggleResponse();"></div>

Or, if you'd like it to realign with respect to the remote based on the
alternate alignment setting:

    <div id="status"{% if alt_align %} class="alt-align"{% endif %} onclick="toggleResponse();"></div>

#### Button Clusters and Buttons
The rest is up to you to design. I'll walk through this using some examples
that include the most pertinent design elements.

##### `.grid-cluster`
Used for a cluster of buttons aligned to a grid. This is likely the most
commonly used container element in a remote.

As an example (not the same remote as the previous example):

    <div class="grid-cluster{% if alt_align %} alt-align{% endif %}">
      <button type="button" onclick="tx(OFF);">Off</button>
      <div></div>
      <button type="button" style="--button-bg: #090;" onclick="tx(ON);">On</button>
    </div>

This presents two buttons, an off button and an on button, separated by an
empty space. The `--button-width`, `--button-height`, and `--button-gap`
variables come into play here behind the scenes. In this case, the remote is
designed to fit three buttons in a row (remember `max-width`?). Alternate
alignment doesn't change the position of the buttons because of the
`<div></div>` empty space.

However, let's say we tweaked this to something like the following:

    <div class="grid-cluster{% if alt_align %} alt-align{% endif %}">
      <button type="button" onclick="tx(OFF);">Off</button>
      <button type="button" style="--button-bg: #090;" onclick="tx(ON);">On</button>
    </div>

In this case, we'd have two buttons and an empty space in a row designed for
three buttons. You'd see the two buttons change alignment depending on the
alternate alignment state. This helps to keep the buttons on the "outside" of
the remote so they're easier to hit with your thumb on a large phone.

You don't need to limit yourself to placing buttons a row at a time. Consider
something like this:

    <div class="grid-cluster{% if alt_align %} alt-align{% endif %}">
      <button type="button" onclick="tx(MEMRY);">Memory</button>
      <button type="button" onclick="tx(LENS1);">Lens1</button>
      <button type="button" onclick="tx(LENS2);">Lens2</button>
      <button type="button" style="font-size: 8pt;" onclick="tx(FRMIN);">Frame Int</button>
      <button type="button" onclick="tx(RGBCM);">RGBCMY</button>
      <button type="button" onclick="tx(PATRN);">Pattern</button>
      <button type="button" onclick="tx(USER);">User</button>
      <button type="button" class="condensed" style="font-size: 8pt; font-stretch: condensed;" onclick="tx(TDFMT);">3D Format</button>
      <button type="button" onclick="tx(ASPCT);">Aspect</button>
    </div>

This is from a remote also designed to fit three buttons in a row. What we see
here is that the buttons automatically flow in the grid three to a row, for a
total of three rows, three columns each.

##### `.directional-cluster`
Often, remotes have a cluster of buttons that are used for navigation, menu
selection, or similar. That's where `.directional-cluster` comes in. Take a
look at this example:

    <div class="directional-cluster{% if alt_align %} alt-align{% endif %}" style="--button-width: 2.5rem; --button-height: 2.5rem; margin: var(--button-gap) calc(var(--button-gap) * 6.5);">
      <div class="directional-up">
        <button type="button" onclick="tx(UP);">▲</button>
      </div>
      <div class="directional-left">
        <button type="button" onclick="tx(LEFT);">◀︎</button>
      </div>
      <div class="directional-select">
        <button type="button" style="border-radius: 0.5ex;" onclick="tx(ENTER);">Enter</button>
      </div>
      <div class="directional-right">
        <button type="button" onclick="tx(RIGHT);">▶︎</button>
      </div>
      <div class="directional-down">
        <button type="button" onclick="tx(DOWN);">▼</button>
      </div>
    </div>

This produces a nice cluster of directional buttons, including proper borders
to simulate shadows. Note the use of `--button-width`, `--button-height`, and
`margin`. These allow you to customize the look of the cluster to fit in with
the remote's design.

##### `.v-rocker-cluster`
Volume buttons, for example, often have a "rocker" appearance, where a single
piece of rubber spans two buttons (volume up and volume down, e.g.).
`.v-rocker-cluster` simulates this look. Here's an example:

    <div class="v-rocker-cluster no-alt" style="margin-left: 0; --button-width: 2.5rem; --button-height: 2.5rem; float: right; width: var(--button-width);">
      <span style="text-align: center;"><br>VOL</span>
      <div class="v-rocker-up">
        <button type="button" onclick="tx(VOLUP);">+</button>
      </div>
      <div class="v-rocker-down">
        <button type="button" onclick="tx(VOLDN);">−</button>
      </div>
    </div>

In this case, note the use of `margin-left` and `float`. This causes the button
cluster to always remain aligned to the right of the remote.

> **Why no `.h-rocker-cluster`?** Oddly, I don't have a single remote in the
  house with horizontal rockers and I don't know if I've ever seen them before.

There is one final CSS element present in this example that hasn't been
mentioned.

#### `.no-alt`
The `no-alt` class is used to prevent alternate alignment from having any
impact. In the `.v-rocker-cluster` example, since this button cluster is meant
to always on the right side of the remote, we do not want it to change position
when alternate alignment is changed.

### Example Remotes
There are a handful of example remotes included. These are remotes I created to
replace physical remotes I use. I encourage you to take a look at those for
inspiration.

## Putting it All Together
Let's take a look at the demo remote. This is made up of four parts.

### `templates/remotes/demo.html`
    {% extends 'remote-base.html' %}
    {% block remote_content %}
        <div>
          <iframe id="response"{% if alt_align %} class="alt-align"{% endif %}></iframe>
          <button id="response-close"{% if alt_align %} class="alt-align"{% endif %} onclick="showResponse(false);">✕</button>
        </div>
        <div id="remote"{% if alt_align %} class="alt-align"{% endif %}>
          <div id="status"{% if alt_align %} class="alt-align"{% endif %} onclick="toggleResponse();"></div>
          <legend{% if alt_align %} class="alt-align"{% endif %}>Demo Remote</legend>
          <div class="grid-cluster alt-align">
            <button type="button" onclick="nop();">A</button>
            <button type="button" class="blue" onclick="invalid();">B</button>      
            <button type="button" onclick="tx(POWER);">C</button>
          </div>
        </div>
    {% endblock %}

### `static/remotes/scipts/demo.js`
    POWER = { 'p': 0x13, 'a': 0x1, 'c': 0x14, 'b': 0xc }

### `static/remotes/css/demo.css`
    .blue {
      --button-bg: #008;
    }

### `static/remotes/images/demo.png`
![Demo remote image.](https://github.com/spakov/irbox_app/blob/main/static/remotes/images/demo.png)

### Config File
    …
    REMOTES = {
    …
      'demo': 'Demo Remote',
    …
    }
    …

### The End Result
The IR box app displays Demo Remote, with accompanying image, on the index
page. Upon navigating to the remote, the HTML is displayed, with associated
JavaScript and CSS automatically included. The `#status` can be clicked/tapped
to toggle display of the `#response` and changes color based on the transmit
state.

Button A transmits a `nop` command, button B (which is blue) transmits an
`invalid` command, and button C transmits the Sony TV power command.

## Other Considerations
### Command Chaining
You may be able to chain multiple commands together to create macro buttons. I
have not tried this, but it will likely work by calling `tx()` multiple times
one after another in a button's `onclick` attribute.

### "Held" Buttons
In some cases, devices respond differently to infrared commands when a button
is held than when it's pressed. An example of this can be found in the
`epson-165652600` remote: the physical remote has a notation that the SWAP
function can be activated by holding the P-in-P button for three seconds. I
took advantage of an empty space and added a SWAP button to achieve this
effect.

It's possible to replicate this by creating a new button with the same command
but a higher number of repeats.

## Future Enhancements
- Support for multiple IR boxes
