<img width="200" height="200" alt="image" src="https://user-images.githubusercontent.com/121936658/215396835-ba7215f7-2051-4953-ac5a-e3818388bfd4.png" />


# ClassicMixer
Restores Classic Volume Mixer On Windows 11 (sndvol).


<img width="600" height="700" alt="image" src="https://github.com/user-attachments/assets/31127227-50ff-4615-b683-af804ca4a7b9" /><img width="700" height="534" alt="image" src="https://github.com/user-attachments/assets/3d50258a-03e5-46a2-ad1f-79bf2d7fe38b" />


## Features

1. Spawn the Classic mixer (sndvol) to bottom right corner of screen by simply clicking the tray icon.


2. Open sound output window to bottom right corner of screen by right clicking tray icon and selecting sound output. 


2. Light Weight.


3. Supports ALL resolutions and screen sizes.


4.Custom sndvol window width can be specified by user by editing `custom_size.ini` width is calculated in pixels.




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


Can run at windows startup.


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

Copyright 2026 7gxycn08

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
