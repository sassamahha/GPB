import argparse
import os
import paramiko


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', required=True)
    parser.add_argument('--level', required=True)
    args = parser.parse_args()

    host = 'partnerupload.google.com'
    user = os.getenv('PB_SFTP_USER')
    key_path = os.getenv('PB_SFTP_KEY')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.RSAKey.from_private_key_file(key_path)
    ssh.connect(host, username=user, pkey=pkey)
    sftp = ssh.open_sftp()

    csv_path = f"csv/{args.lang}_{args.level}.csv"
    epub_path = f"epub/{args.lang}_{args.level}.epub"
    cover_path = f"assets/cover_{args.level}.jpg"

    sftp.put(csv_path, f"/csv/{os.path.basename(csv_path)}")
    sftp.put(epub_path, f"/epub/{os.path.basename(epub_path)}")
    sftp.put(cover_path, f"/cover/{os.path.basename(cover_path)}")

    sftp.close()
    ssh.close()


if __name__ == '__main__':
    main()
