# PyBoot
Script for tether booting Checkm8 vulnerable iOS devices by Matty [(moski)](https://twitter.com/mosk_i)

## DISCLAIMER

MACOS ONLY - Don't ask for Windows support

Don't use this on a main device, expect issues, bugs and other problems that will make this a bad experience. In saying that, it should work without any major issues, but I'd rather have this disclaimer so I have an excuse to ignore wen eta kids.

## What is PyBoot?

PyBoot is a simple alternative to ra1nsn0w for tether booting Checkm8 vulnerable iOS devices. It downloads and patches iBSS/iBEC, downloads the Kernel, DeviceTree and TrustCache for the downgraded version, patches the type to the restore type (E.G krnl -> rkrn, etc) and signs them with SHSH, then sends the images to the device and boots them! PyBoot also has support for devices which have key pages on theiphonewiki with multiple platforms (E.G 6s with N71AP and N71mAP), which ra1nsn0w currently doesn't support. 

PyBoot is most likely extremely broken, expect issues and bugs. I just made this for fun, and to have an alternative to ra1nsn0w for booting tethered downgraded devices with SuccessionDown (my Succession fork for tethered downgrades on-device).

How do I tether downgrade my device you might be asking? Simply add my repo (matthewpierson.github.io) to Cydia/Zebra/Sileo and install "SuccessionDown" =)

Feel free to create a pull request if you want to help improve this, or create an issue if you find one!

If you wish to donate to me, feel free to do so, but donations are in no way required or expected. My paypal account is matthewpierson01@gmail.com (I can't create a paypal.me link in New Zealand sadly, so you'd need to send donations manually). I make these things for fun and to be useful to the jailbreak community, not for profit, but money is still nice =)

## Current device/iOS support

iOS support is detirmened by what SEP you currently have installed. For example, if you have iOS 12.3 installed (not futurerestored) with 12.3's SEP, then you can downgrade to any iOS version that 12.3's SEP is compatible with. The list below is based off the latest SEP (13.3.1/12.4.5) but you might be able to downgrade to other versions.

- iPhone 5s - 11.3 -> 12.4.5
- iPhone 6/6+ - 11.3 -> 12.4.5
- iPhone 6s/6s+ - 13.0 -> 13.3.1
- iPhone SE - 13.0 -> 13.3.1
- iPhone 7/7+ - 13.0 -> 13.3.1
- iPhone 8/8+ - 13.0 -> 13.3.1 (Untested)
- iPhone X - 13.0 -> 13.3.1 (Currently broken)

All iPads and iPods are untested, but they should work fine with the corresponding iPhone CPU. Please try and let me know if they work or not.

Currently iPhone X support is broken (kernel panicking 30~ seconds after booting). Keep in mind that even after X support is added, Face-ID will be broken no matter what version you go to (with minor exceptions). Touch-ID works fine on all supported versions.

## Usage
```
Usage: ./pyboot.py [OPTIONS]

E.G "./pyboot.py -i iPhone8,1 13.2.3 -b ~/Downloads/bootlogo.png"

Options:

  -i, --ios DEVICE IOS		Device model and downgraded iOS version to boot
  -q, --ipsw IPSW DEVICE  Path to downloaded IPSW
  -b, --bootlogo LOGO 		Path to .PNG to use as boot logo
  -p, --pwn		            Enter PWNDFU mode, which will also apply sig patches
  -d, --dualboot          Name of system partition you wish to boot (e.g disk0s1s3 or disk0s1s6)
  -a, --bootargs          Custom boot-args, will prompt user to enter, don't enter a value upon running PyBoot (Default is '-v')
  -c, --credits			      Show credits
  -v, --version			      List the version of PyBoot

```

## Instructions

1. cd into the PyBoot directory
2. Run pip3 install -r requirements.txt
3. Connect your device in DFU mode to your computer
4. Run PyBoot with your desiered options - E.G './pyboot.py -i iPhone8,1 13.1.1 -b ~/Downloads/customBootLogo.png'
5. Run PyBoot whenever you want to boot the device
6. Enjoy! 

## Upcoming Features

- Custom bootargs

- More super secret stuff =)

## Known Issues

- Very high storage usage after downgrading. Can be partially mitigated with a "Reset content and settings" (mobile_obliterator is called after the downgrade by successiondown but sometimes it doesn't run) You could also try [this](https://github.com/MatthewPierson/PyBoot/issues/2) but I haven't tested this so you'd be on your own.

- Some IPSW's won't download from Apple's servers. Can be avoided by either picking a different iOS version or by providing a rootfs dmg in the correct folder

- ~~Jailbreak's don't work after downgrading. No current method to jailbreak devices downgraded by this method. Checkra1n will give OTA error when installing Cydia (Might be possible to fix) and Unc0ver fails when attempting to find kernel offsets (Probably can't fix)~~ Unc0ver 4.1.0 and higher should work fine for jailbreaking 13.x - 13.3, you still can't use Checkra1n however as that will cause broken WiFi on boot, plus other issues. Electra does work for jailbreaking 11.x, but has some issues that you can fix by following [this tweet from coolstar](https://twitter.com/CStar_OW/status/1233241107661615108) after jailbreaking. 12.x jailbreaks are untested, will edit README with info later.

- Some iOS versions won't boot due to SEP incompatibilities. I have this partially mitigated by including a check for whether SEP is compatible or not, but obviously this is bypassable. 

## Help, PyBoot is giving me errors!

- First make sure you have ran "pip3 install -r requirements.txt" before doing anything

- If you are getting irecovery related errors, download [this bash script](https://gist.github.com/MatthewPierson/3838e6192120f27b195b2f284f5737c6) and run it 

## Credits

Me - For writing this whole thing :)

Thimstar - [img4tool](https://github.com/tihmstar/img4tool), [iBoot64Patcher](https://github.com/tihmstar/iBoot64Patcher), [tsschecker](https://github.com/tihmstar/tsschecker)

realnp - [ibootim](https://github.com/realnp/ibootim)

axi0mX - [ipwndfu/checkm8](https://github.com/axi0mX/ipwndfu)

dayt0n - [kairos](https://github.com/dayt0n/kairos)

Marco Grassi - [PartialZip](https://github.com/marcograss/partialzip)

Merculous - [ios-python-tools](https://github.com/Merculous/ios-python-tools) (iphonewiki.py for keys)

0x7ff - [Eclipsa](https://github.com/0x7ff/eclipsa)

libimobiledevice team - [irecovery](https://github.com/libimobiledevice/libirecovery)

