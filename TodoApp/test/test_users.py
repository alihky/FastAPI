from .utils import *
from fastapi import status
from ..routers.users import get_db, get_current_user # 👈 تأكد من كتابة هذا السطر بدقة

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
# 1. اختبار جلب بيانات المستخدم بنجاح
def test_return_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == "codingwithrobytest"
    assert response.json()['email'] == "codingwithrobytest@email.com"
    assert response.json()['first_name'] == "Eric"
    assert response.json()['last_name'] == "Roby"
    assert response.json()['role'] == "admin"
    assert response.json()['phone_number'] == "(111)-111-1111"

# 2. اختبار تغيير كلمة المرور بنجاح
def test_change_password_success(test_user):
    response = client.put("/user/password", json={"password": "testpassword",
                                                  "new_password": "newpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT

# 3. اختبار فشل تغيير كلمة المرور عند إدخال كلمة مرور الحالية خاطئة
def test_change_password_invalid_current_password(test_user):
    response = client.put("/user/password", json={"password": "wrong_password",
                                                  "new_password": "newpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}

# 4. اختبار تغيير رقم الهاتف بنجاح
def test_change_phone_number_success(test_user):
    response = client.put("/user/phonenumber/2222222222")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    

