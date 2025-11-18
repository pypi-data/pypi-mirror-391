# FT8 Stack for inventree

**I will not be providing support to those who can't get this to work on-the-air. This is more of a proof of concept and not an actual product. Don't create issues or send me e-mails about it not working.**

This is a silly little project that I started to help me learn how to work on building within the React-based interface that Inventree started using after 1.0. 

![Demo](demo.png "Demo")

In theory, everything should work to communicate using FT8. As of publishing this, this may be the only client on the web that does this right now that runs completely in one's browser. 

As of 0.0.1, CAT control functionality does not exist. You would in theory need to enable VOX or manually key up if you intend on testing this.

## Usage

Install the plugin either from this git url or on PyPi: `inventree_ft8`. Make sure to restart inventree after installing and enabling.

When you install the plugin, it will create a new frontend page on the user settings page. I want to get the navigation bar functionality to work, but I think it's either not fully functional or I did something in my implementation wrong.

## Building

**NOTE:** The FT8JS library will want to pull it's assets from the URL root instead of the inventree static plugin root, this is baked into the library and you must edit the exported FT8Panel.js and find and replace `/assets` with `/static/plugins/ft8/assets`.