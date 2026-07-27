import uuid
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q

from accounts.models import SubscriptionPlan, PaymentTransaction, OwnerSubscriptionHistory
from accounts.serializers import PaymentTransactionSerializer, OwnerSubscriptionHistorySerializer
from accounts.paginations import StandardResultsSetPagination
from accounts.utils.mmpay_client import MMPay


# ==========================================
# 1. Initiate Payment (Create QR for MMPay)
# ==========================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """
    Owner က Plan ဝယ်ရန် နှိပ်လိုက်သောအခါ MMPay မှ EMVCo MMQR String ကို ထုတ်ပေးမည်
    - Body: { "plan_id": "uuid-string" }
    """
    user = request.user
    if not hasattr(user, 'owner_profile'):
        return Response({"error": "သင့်တွင် Owner Profile မရှိသေးပါ။"}, status=status.HTTP_400_BAD_REQUEST)

    owner = user.owner_profile
    plan_id = request.data.get('plan_id')

    try:
        plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
    except SubscriptionPlan.DoesNotExist:
        return Response({"error": "ရွေးချယ်ထားသော Plan ကို ရှာမတွေ့ပါ။"}, status=status.HTTP_404_NOT_FOUND)

    # Unique Order ID ဖန်တီးခြင်း
    merchant_order_id = f"ORD-{uuid.uuid4().hex[:10].upper()}"

    # Database ထဲတွင် PENDING အနေဖြင့် မှတ်တမ်းတင်ခြင်း
    transaction = PaymentTransaction.objects.create(
        owner=owner,
        plan=plan,
        merchant_order_id=merchant_order_id,
        amount=plan.price,
        payment_status='PENDING'
    )

    try:
        # MMPay SDK မှ pay() ကို ခေါ်ဆိုခြင်း
        mmpay_response = MMPay.pay({
            "orderId": merchant_order_id,
            "amount": int(plan.price)
        })

        return Response({
            "message": "ငွေပေးချေရန် QR ကုဒ် အောင်မြင်စွာ ထုတ်ယူပြီးပါပြီ။",
            "merchant_order_id": merchant_order_id,
            "amount": plan.price,
            "status": mmpay_response.get('status'),
            "qr": mmpay_response.get('qr'), 
            "vendor_qr_ref_id": mmpay_response.get('vendorQrRefId'),
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        transaction.payment_status = 'FAILED'
        transaction.save()
        return Response({"error": f"MMPay Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==========================================
# 2. MMPay Webhook / Callback Handler
# ==========================================
def handle_success(tx):
    order_id = tx.get('orderId')
    transaction_ref_id = tx.get('transactionRefId')

    try:
        transaction = PaymentTransaction.objects.select_related('owner', 'plan').get(merchant_order_id=order_id)
        
        if transaction.payment_status != 'SUCCESS':
            transaction.payment_status = 'SUCCESS'
            transaction.transaction_id = transaction_ref_id
            transaction.paid_at = timezone.now()
            
            duration = transaction.plan.duration_days
            expires_at = timezone.now() + timedelta(days=duration)
            transaction.expires_at = expires_at
            transaction.save()

            owner = transaction.owner
            tx_type = 'NEW'
            if owner.current_plan:
                tx_type = 'RENEW'

            owner.current_plan = transaction.plan
            owner.plan_expires_at = expires_at
            owner.save()

            OwnerSubscriptionHistory.objects.create(
                owner=owner,
                plan=transaction.plan,
                payment_transaction=transaction,
                transaction_type=tx_type,
                start_date=timezone.now(),
                end_date=expires_at,
                amount_paid=transaction.amount
            )
            print(f"Webhook Success processed for Order: {order_id}")
    except PaymentTransaction.DoesNotExist:
        print(f"Transaction not found for Order ID: {order_id}")

def handle_fail(tx):
    order_id = tx.get('orderId')
    PaymentTransaction.objects.filter(merchant_order_id=order_id).update(payment_status='FAILED')

def handle_cancel(tx):
    order_id = tx.get('orderId')
    PaymentTransaction.objects.filter(merchant_order_id=order_id).update(payment_status='FAILED')

MMPay.on_tx_success(handle_success)
MMPay.on_tx_fail(handle_fail)
MMPay.on_tx_cancel(handle_cancel)


@csrf_exempt
def mmpay_webhook(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    payload_str = request.body.decode('utf-8')
    nonce = request.headers.get('X-Mmpay-Nonce')
    signature = request.headers.get('X-Mmpay-Signature')

    if not nonce or not signature:
        return JsonResponse({"error": "Missing headers"}, status=400)

    try:
        MMPay.listen(payload_str, nonce, signature)
        return JsonResponse({"received": True}, status=200)
    except Exception as e:
        print("Webhook verification failed:", e)
        return JsonResponse({"error": "Invalid signature"}, status=400)


# ==========================================
# 3. Transaction & History List Views
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_transaction_list(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        transactions = PaymentTransaction.objects.select_related('owner__user', 'plan').all().order_by('-id')
    else:
        if not hasattr(user, 'owner_profile'):
            return Response({"error": "သင့်တွင် Owner Profile မရှိသေးပါ။"}, status=status.HTTP_403_FORBIDDEN)
        transactions = PaymentTransaction.objects.select_related('owner__user', 'plan').filter(owner=user.owner_profile).order_by('-id')

    paginator = StandardResultsSetPagination()
    paginated_data = paginator.paginate_queryset(transactions, request)
    serializer = PaymentTransactionSerializer(paginated_data, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_history_list(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        histories = OwnerSubscriptionHistory.objects.select_related('owner__user', 'plan', 'payment_transaction').all().order_by('-created_at')
    else:
        if not hasattr(user, 'owner_profile'):
            return Response({"error": "သင့်တွင် Owner Profile မရှိသေးပါ။"}, status=status.HTTP_403_FORBIDDEN)
        histories = OwnerSubscriptionHistory.objects.select_related('owner__user', 'plan', 'payment_transaction').filter(owner=user.owner_profile).order_by('-created_at')

    paginator = StandardResultsSetPagination()
    paginated_data = paginator.paginate_queryset(histories, request)
    serializer = OwnerSubscriptionHistorySerializer(paginated_data, many=True)
    return paginator.get_paginated_response(serializer.data)