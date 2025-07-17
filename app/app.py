import os
import boto3
import uuid
from flask import Flask, request, render_template, redirect, url_for, flash, Response
from botocore.exceptions import ClientError, NoCredentialsError

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Cấu hình AWS S3
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
S3_REGION = os.environ.get('S3_REGION', 'ap-northeast-1')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Định dạng file được phép
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_s3_client():
    """Tạo S3 client với error handling"""
    try:
        return boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=S3_REGION
        )
    except Exception as e:
        print(f"Lỗi khi tạo S3 client: {e}")
        return None

def list_s3_files():
    """Liệt kê files trong S3 bucket"""
    s3_client = get_s3_client()
    if not s3_client:
        return []
    
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET)
        files = []
        for obj in response.get('Contents', []):
            files.append({
                'name': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified']
            })
        return files
    except ClientError as e:
        print(f"Lỗi khi liệt kê files: {e}")
        flash(f'Lỗi khi liệt kê files: {str(e)}', 'error')
        return []

def upload_to_s3(file, filename):
    """Upload file lên S3"""
    s3_client = get_s3_client()
    if not s3_client:
        return False
    
    try:
        s3_client.upload_fileobj(file, S3_BUCKET, filename)
        return True
    except ClientError as e:
        print(f"Lỗi upload: {e}")
        flash(f'Lỗi upload: {str(e)}', 'error')
        return False

def download_from_s3(filename):
    """Download file từ S3"""
    s3_client = get_s3_client()
    if not s3_client:
        return None
    
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=filename)
        return response['Body'].read()
    except ClientError as e:
        print(f"Lỗi download: {e}")
        flash(f'Lỗi download: {str(e)}', 'error')
        return None

def delete_from_s3(filename):
    """Xóa file khỏi S3"""
    s3_client = get_s3_client()
    if not s3_client:
        return False
    
    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=filename)
        return True
    except ClientError as e:
        print(f"Lỗi xóa: {e}")
        flash(f'Lỗi xóa: {str(e)}', 'error')
        return False

@app.route('/')
def index():
    """Trang chủ"""
    files = list_s3_files()
    return render_template('index.html', files=files, bucket_name=S3_BUCKET)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload file"""
    if 'file' not in request.files:
        flash('Không có file được chọn!', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Không có file được chọn!', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # Tạo tên file unique
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        
        if upload_to_s3(file, filename):
            flash(f'Upload thành công: {file.filename}', 'success')
        else:
            flash('Lỗi khi upload file!', 'error')
    else:
        flash('Định dạng file không được hỗ trợ!', 'error')
    
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    """Download file"""
    file_data = download_from_s3(filename)
    if file_data:
        return Response(
            file_data,
            mimetype='application/octet-stream',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    flash('Không thể tải file!', 'error')
    return redirect(url_for('index'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    """Xóa file"""
    if delete_from_s3(filename):
        flash(f'Đã xóa: {filename}', 'success')
    else:
        flash('Không thể xóa file!', 'error')
    return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check cho Kubernetes"""
    return {
        'status': 'healthy',
        'bucket': S3_BUCKET,
        'region': S3_REGION
    }, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
