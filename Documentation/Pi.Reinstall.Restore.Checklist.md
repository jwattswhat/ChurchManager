# Raspberry Pi MariaDB Reinstall and Restore Checklist

Do not erase or reimage the Raspberry Pi until both backup files below have been
copied to at least one additional storage device.

## Verified recovery files

| Database | Backup file | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| ChurchDB | `BackupDB/ChurchDB.pre-test.2026-08-09.073820.sql` | 153,915,874 | `AE85BE438ACF248AA77B8C29FEE5D2A6FBE6BF0BDB36D10BE74678174654A0BF` |
| JSForm | `BackupDB/JSForm.pre-pi-reinstall.2026-08-09.181359.sql` | 21,635 | `98F095BB00BFF53B7FAC1812AF59B9616CAE35EC79C41A9B10691A2B5942EA7B` |

Both files were checked for nonzero size and MariaDB's dump-completion marker.

## 1. Before reinstalling

- Copy both SQL files to another physical drive.
- Keep the ChurchManager application folder on Windows unchanged.
- Record the Pi's current address (`192.168.3.200`) and hostname (`lic`).
- Plan to reuse the existing ChurchManager database password from the protected
  local configuration. Do not write that password into this checklist.

## 2. Reinstall the Pi

- Use Raspberry Pi Imager to install a current 64-bit Raspberry Pi OS or other
  supported Debian-based image.
- Before writing the card, open the imager's OS customization settings, set
  hostname `lic`, create an administrator user, and **enable SSH** with password
  or key authentication. Treat SSH as required, not optional.
- Preserve address `192.168.3.200` with a router reservation or static network
  configuration.

After first boot, connect from Windows PowerShell:

```powershell
ssh <pi-user>@192.168.3.200
```

If the connection fails, attach a keyboard and monitor to the Pi and run:

```bash
sudo systemctl enable --now ssh
sudo systemctl status ssh
```

From Windows, verify that port 22 is reachable and that an interactive login
works:

```powershell
Test-NetConnection 192.168.3.200 -Port 22
ssh <pi-user>@192.168.3.200
```

Do not begin the MariaDB installation or restoration until `TcpTestSucceeded`
is `True` and the SSH login succeeds.

## 3. Install and start MariaDB

Run on the Pi:

```bash
sudo apt update
sudo apt install mariadb-server
sudo systemctl enable --now mariadb ssh
sudo mariadb-secure-installation
```

## 4. Create empty databases

Run on the Pi:

```bash
sudo mariadb
```

Then run:

```sql
CREATE DATABASE ChurchDB CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE DATABASE JSForm CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE DATABASE ChurchDBTest CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
exit
```

## 5. Copy backups to the Pi

Run from the ChurchManager folder in Windows PowerShell:

```powershell
scp "BackupDB\ChurchDB.pre-test.2026-08-09.073820.sql" <pi-user>@192.168.3.200:/home/<pi-user>/
scp "BackupDB\JSForm.pre-pi-reinstall.2026-08-09.181359.sql" <pi-user>@192.168.3.200:/home/<pi-user>/
```

## 6. Restore the databases

Run on the Pi:

```bash
sudo mariadb ChurchDB < ~/ChurchDB.pre-test.2026-08-09.073820.sql
sudo mariadb JSForm < ~/JSForm.pre-pi-reinstall.2026-08-09.181359.sql
sudo mariadb ChurchDBTest < ~/ChurchDB.pre-test.2026-08-09.073820.sql
```

## 7. Recreate ChurchManager database access

Run `sudo mariadb` on the Pi. Replace the placeholder with the password already
stored in the protected ChurchManager configuration on Windows:

```sql
CREATE USER IF NOT EXISTS 'church'@'%' IDENTIFIED BY '<existing ChurchManager password>';
GRANT ALL PRIVILEGES ON ChurchDB.* TO 'church'@'%';
GRANT ALL PRIVILEGES ON JSForm.* TO 'church'@'%';
GRANT ALL PRIVILEGES ON ChurchDBTest.* TO 'church'@'%';
FLUSH PRIVILEGES;
SHOW GRANTS FOR 'church'@'%';
```

Do not place the real password in documentation, shell history, or source control.

## 8. Permit LAN connections

On the Pi, edit MariaDB's server configuration and set `bind-address` to the Pi's
LAN address or an appropriate LAN-listening value. Restart MariaDB afterward:

```bash
sudo systemctl restart mariadb
sudo systemctl status mariadb
```

If a firewall is active, permit TCP port 3306 only from the trusted Windows
computer or local subnet. Do not expose MariaDB to the internet.

## 9. Verify before using ChurchManager

From Windows PowerShell:

```powershell
& "C:\Program Files\MariaDB 12.1\bin\mariadb.exe" --host=192.168.3.200 --port=3306 --user=church --password --skip-ssl ChurchDB
```

Confirm representative families, people, services, sermons, prayers, and reports.
Then run the automated ChurchManager suite against `ChurchDBTest`. Do not delete
the Windows backups after a successful restore.
