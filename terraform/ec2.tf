resource "aws_instance" "nc_plus_one" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"
  key_name      = "nc_plus_one_dev"

  vpc_security_group_ids = [
    aws_security_group.nc_plus_one.id,
    aws_security_group.nc_plus_one_http.id
  ]

  user_data = <<-EOF
    #!/bin/bash

    apt-get update
    apt-get install -y git python3 python3-venv python3-pip

    git clone https://github.com/johnnybquintero-ui/nc-plus-one.git /home/ubuntu/nc-plus-one
    cd /home/ubuntu/nc-plus-one

    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt

    export PGHOST=localhost
    export PGPORT=5432
    export PGDATABASE=nc_plus_one
    export PGUSER=ubuntu
    export PGPASSWORD=
    export JWT_SECRET=temporary-dev-secret

    nohup .venv/bin/uvicorn main:app \
      --host 0.0.0.0 \
      --port 8000 \
      > /var/log/nc-plus-one.log 2>&1 &
  EOF

  user_data_replace_on_change = true

  tags = {
    Name = "nc-plus-one-dev"
  }
}