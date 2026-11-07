# MyKOS — Technical Architecture

- Status: Proposed baseline — v1.0
- Scope: Initial x86_64 desktop distribution
- Related: Product Vision and Roadmap in this directory

## 1. Architecture goals

MyKOS will be a Linux distribution assembled from established upstream components, with a focused integration layer and a distinctive user experience.

The architecture should:

- Keep the Linux base replaceable where practical.
- Separate desktop presentation from privileged system operations.
- Prefer stable upstream interfaces such as D-Bus and documented command-line APIs.
- Minimize long-lived forks and private patches.
- Make builds reproducible and releases testable.
- Use least privilege for all system-management operations.

## 2. Logical architecture

    +-------------------------------------------------------------+
    |                    MyKOS Experience Layer                  |
    | Desktop shell | Settings | App Catalog | File Manager       |
    | Notifications | Developer tools integration                 |
    +-----------------------------+-------------------------------+
                                  |
    +-----------------------------v-------------------------------+
    |                    MyKOS Platform Layer                     |
    | System API | App integration | Update UX | Device UX        |
    | Configuration | Diagnostics | MyKOS-specific policy         |
    +-----------------------------+-------------------------------+
                                  |
    +-----------------------------v-------------------------------+
    |                    Linux System Services                    |
    | systemd | D-Bus | Polkit | NetworkManager | PipeWire         |
    | UDisks2 | fwupd (where supported) | system services         |
    +-----------------------------+-------------------------------+
                                  |
    +-----------------------------v-------------------------------+
    |                    Linux Desktop Platform                   |
    | KDE Plasma | KWin | Wayland | Qt 6/QML | Mesa                |
    +-----------------------------+-------------------------------+
                                  |
    +-----------------------------v-------------------------------+
    |                    Linux Base and Hardware                  |
    | Linux kernel | GNU/userland | libraries | firmware | devices |
    +-------------------------------------------------------------+

This is a logical view, not a strict packaging or process boundary. KDE Plasma, KWin, Wayland, Qt, and Mesa occupy different positions in the real graphics and desktop stack. The diagram groups them to communicate the platform relationship.

## 3. Initial technology baseline

| Area | Proposed choice | Notes |
|---|---|---|
| Distribution base | Ubuntu LTS | Select and pin a specific supported LTS release when implementation starts. |
| Architecture | x86_64 | Initial target; other architectures are future work. |
| Desktop | KDE Plasma | Integrate upstream first; avoid a full fork. |
| Display protocol | Wayland | Retain compatibility paths where hardware or applications require them. |
| Window manager/compositor | KWin | Upstream KDE component. |
| UI framework | Qt 6 / QML | For MyKOS desktop components and applications. |
| New system services | Rust | Preferred for new privileged or background services when appropriate. |
| System integration | D-Bus | Use documented interfaces and narrow service contracts. |
| Authorization | Polkit | Enforce authorization for privileged actions. |
| Init/service manager | systemd | Use upstream service management. |
| Networking | NetworkManager | Use existing desktop/system integration. |
| Audio | PipeWire | Use upstream audio stack. |
| Storage/device integration | UDisks2 and udev | Use upstream interfaces. |
| Firmware | fwupd | Only for supported devices and update sources. |
| System packages | APT / DEB | Base OS and system-level components. |
| Desktop applications | Flatpak | Primary graphical application distribution candidate. |
| Installer | Calamares | Validate integration, branding, and compatibility with the chosen base. |
| Image build | Ubuntu-compatible image build pipeline | Choose a maintained tool and pin versions during M0. |
| Virtual testing | QEMU/KVM | Primary repeatable VM test environment. |

The table is a proposal, not a claim that every component is already integrated. Exact versions and compatibility constraints must be pinned in the build configuration.

## 4. Distribution layer

The distribution layer owns:

- Base package selection and package repositories.
- Kernel and firmware policy.
- Desktop defaults and branding.
- Installer configuration.
- Default applications.
- Image creation and release artifacts.
- Supported hardware definition.

Keep distribution configuration declarative wherever possible. Record package versions, repository origins, build tool versions, and image metadata for each release.

## 5. Desktop experience layer

Start with upstream KDE Plasma and configure it to provide a coherent MyKOS experience.

Initial responsibilities:

- Theme, icons, fonts, wallpaper, panel, and launcher defaults.
- First-run experience and sensible defaults.
- MyKOS settings entry points where upstream settings are insufficient.
- Integration of notifications, shortcuts, accessibility, and power behavior.

Do not fork all of Plasma. If a MyKOS-specific shell or launcher is justified later, build it as a focused component with a clear upstream compatibility strategy.

## 6. MyKOS Platform Layer

This layer is the primary place for MyKOS-specific integration. It should provide stable, narrow contracts to the UI while delegating actual system work to upstream services.

Candidate modules:

| Module | Responsibility | Likely integration |
|---|---|---|
| system-info | OS, kernel, hardware and diagnostic information | procfs, sysfs, D-Bus, standard tools |
| display-integration | Display configuration UX | KWin/desktop interfaces |
| network-integration | Network status and user actions | NetworkManager D-Bus |
| user-integration | User/account workflows | system services and Polkit |
| application-manager | Installed apps and software sources | APT, Flatpak |
| update-manager | Update discovery and user-facing workflow | APT and Flatpak update mechanisms |
| device-integration | Device discovery and status | udev, UDisks2, fwupd |
| power-integration | Battery and power status | UPower and desktop services |
| diagnostics | Collect user-approved logs and health information | journalctl and system interfaces |

These are candidate modules, not a requirement to create one daemon per feature. Prefer a small number of cohesive services over excessive microservices.

### API contract

- Define versioned interfaces and explicit error types.
- Prefer D-Bus for communication with system services.
- Validate all inputs at service boundaries.
- Keep UI processes unprivileged.
- Require Polkit authorization for privileged actions.
- Do not expose arbitrary root command execution to the UI.
- Log security-relevant operations without collecting unnecessary personal data.
- Provide timeouts, cancellation behavior, and clear status reporting.

Illustrative flow for changing a system setting:

1. The unprivileged settings UI submits a typed request.
2. The platform service validates the request.
3. The service checks authorization where required.
4. The service calls the appropriate upstream API.
5. The service returns a structured success or error result.
6. The UI explains the outcome and offers a safe next step.

The example is conceptual; implementation must use the actual supported interfaces of the selected upstream components.

## 7. Application and package strategy

Use different delivery mechanisms for different responsibilities:

- **APT/DEB:** Base OS, drivers, system libraries, and tightly integrated system components.
- **Flatpak:** Preferred route for many desktop applications, with clear source and permission information.
- **Developer tools:** Support standard distribution packages, upstream installers, language version managers, and containers according to documented security guidance.

The MyKOS application catalog should present a consistent user experience while clearly identifying the underlying source, publisher, permissions, and update mechanism.

Do not create a proprietary package format in the initial milestones.

## 8. Updates, recovery, and reliability

Initial release strategy:

- Use the base distribution's supported package update mechanisms.
- Separate OS updates from Flatpak application updates in both implementation and user messaging.
- Test interrupted updates and recovery procedures.
- Provide clear release notes and known-issue information.
- Evaluate Btrfs snapshots and Snapper for rollback only after filesystem, installer, bootloader, and update integration are validated together.
- Evaluate image-based approaches such as bootc only as a later architecture decision, not as an assumed MVP dependency.

A snapshot is not a backup. User data protection and backup guidance must remain separate from system rollback.

## 9. Security model

- Default to unprivileged user sessions.
- Use Polkit and narrow privileged service interfaces.
- Do not embed credentials or secrets in images or repositories.
- Prefer signed packages and trusted repositories.
- Make application permissions understandable.
- Keep the kernel, base packages, and desktop stack on supported update channels.
- Minimize background services and exposed interfaces.
- Publish a vulnerability reporting process before public release.

## 10. Build, test, and release engineering

The build pipeline should:

1. Start from a pinned base release and package manifest.
2. Resolve packages from declared repositories.
3. Apply version-controlled MyKOS configuration and branding.
4. Build a bootable ISO.
5. Generate checksums and build metadata.
6. Run automated image and boot smoke tests.
7. Store logs and artifacts for each build.

Testing layers:

- Static checks for configuration and scripts.
- Package and dependency validation.
- ISO boot tests in QEMU/KVM.
- Installation tests to a clean virtual disk.
- Desktop smoke tests after first boot.
- Update and recovery tests.
- Hardware testing on a documented representative device matrix.

A release must not be considered validated solely because the ISO builds successfully.

## 11. Repository structure

Proposed monorepo structure; create directories as implementation begins:

    mykos/
    ├── docs/
    │   ├── PRODUCT_VISION.md
    │   ├── ARCHITECTURE.md
    │   ├── ROADMAP.md
    │   └── ADR/
    ├── distribution/
    │   ├── base/
    │   ├── packages/
    │   ├── repositories/
    │   ├── installer/
    │   ├── branding/
    │   └── image-build/
    ├── desktop/
    │   ├── shell/
    │   ├── launcher/
    │   ├── settings/
    │   ├── notification-center/
    │   └── components/
    ├── platform/
    │   ├── system-info/
    │   ├── application-manager/
    │   ├── update-manager/
    │   ├── device-manager/
    │   └── system-api/
    ├── applications/
    │   ├── app-store/
    │   └── developer-center/
    ├── services/
    ├── tests/
    │   ├── integration/
    │   ├── hardware/
    │   └── desktop/
    └── scripts/
        ├── build/
        ├── development/
        └── release/

## 12. Architecture decision process

Record decisions that materially affect compatibility, security, packaging, or long-term maintenance in docs/ADR/.

Each ADR should include:

- Context and problem.
- Options considered.
- Decision and rationale.
- Consequences and migration path.
- Date and status.

Revisit a decision when new evidence materially changes its assumptions.
