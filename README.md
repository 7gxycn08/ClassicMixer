<img width="100" height="200" alt="image" src="https://user-images.githubusercontent.com/121936658/215396835-ba7215f7-2051-4953-ac5a-e3818388bfd4.png" />


# ClassicMixer
Restores Classic Volume Mixer On Windows 11 (sndvol).


<img width="500" height="700" alt="image" src="https://github.com/user-attachments/assets/31127227-50ff-4615-b683-af804ca4a7b9" /><img width="500" height="834" alt="image" src="https://github.com/user-attachments/assets/3d50258a-03e5-46a2-ad1f-79bf2d7fe38b" />


## Features

1. Spawn the Classic mixer (sndvol) to bottom right corner of screen by simply clicking the tray icon.


2. Open sound output window to bottom right corner of screen by right clicking tray icon and selecting sound output. 


2. Light Weight.


3. Supports ALL resolutions and screen sizes.


Compiled as a windows executable only using pyinstaller check `releases` or self compile.


For help on how to build manually open a new issue.


Icon taken from `https://www.freepik.com/`

## Usage
`v2.4 and lower` If `SndVol` does not show up when clicking tray icon that means `ClassicMixer` is missing a required dependency which can be found here [.NET 6.0.36](https://builds.dotnet.microsoft.com/dotnet/Runtime/6.0.36/dotnet-runtime-6.0.36-win-x64.exe)


For keyboard shortcuts toggle `Enable Shortcuts` from system tray.


- Volume Up: `CTRL + ALT + UP`
- Volume Down: `CTRL + ALT + DOWN`
- Cycle through Audio output devices: `CTRL + ALT + LEFT` and `CTRL + ALT + RIGHT`


To disable auto close mixer when clicking away toggle `Movable Audio Window` from system tray.


You can use Windows Task Scheduler to run at startup.


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

MIT License

Copyright (c) 2025 7gxycn08

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
