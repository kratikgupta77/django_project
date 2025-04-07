from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Artifact, PaymentTransaction, Wallet
from .forms import ArtifactForm  
@login_required
def marketplace_home(request):
    """
    Landing page for the marketplace with options to sell, buy, or view payment history.
    """
    return render(request, "marketplace/landing.html")

@login_required
def sell_item(request):
    """
    Display a form to list a new artifact.
    """
    if request.method == "POST":
        form = ArtifactForm(request.POST, request.FILES)
        if form.is_valid():
            artifact = form.save(commit=False)
            artifact.seller = request.user.userprofile  
            artifact.save()
            return redirect('marketplace:artifact_detail', pk=artifact.pk)
    else:
        form = ArtifactForm()
    return render(request, "marketplace/sell_item.html", {'form': form})

@login_required
def artifact_list(request):
    """
    List all artifacts with optional search.
    """
    query = request.GET.get('q')
    if query:
        artifacts = Artifact.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        artifacts = Artifact.objects.all()
    return render(request, "marketplace/artifact_list.html", {'artifacts': artifacts, 'query': query})

@login_required
def artifact_detail(request, pk):
    """
    Display details for a single artifact.
    """
    artifact = get_object_or_404(Artifact, pk=pk)
    return render(request, "marketplace/artifact_detail.html", {'artifact': artifact})



from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64

def verify_signature(public_key_pem, message, signature_b64):
    public_key = serialization.load_pem_public_key(public_key_pem.encode())
    signature = base64.b64decode(signature_b64)
    try:
        public_key.verify(
            signature,
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

@login_required
def payment_history(request):
    """
    Display a list of payment transactions where the user is either the buyer or seller.
    """
    user_profile = request.user.userprofile
    transactions = PaymentTransaction.objects.filter(
        Q(buyer=user_profile) | Q(seller=user_profile)
    ).order_by('-created_at')
    return render(request, "marketplace/payment_history.html", {'transactions': transactions})


from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64

def sign_message(private_key_pem: str, message: str) -> str:
    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    signature = private_key.sign(
        message.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@login_required
@csrf_exempt
def upload_public_key(request):
    if request.method == "POST":
        data = json.loads(request.body)
        public_key = data.get("public_key")
        if public_key:
            request.user.userprofile.public_key = public_key
            request.user.userprofile.save()
            return JsonResponse({"status": "success"})
        return JsonResponse({"error": "Missing key"}, status=400)
@login_required
def simulate_payment(request, pk):
    artifact = get_object_or_404(Artifact, pk=pk)
    buyer_profile = request.user.userprofile
    seller_profile = artifact.seller

    # Prevent self-purchase or duplicate purchase
    if buyer_profile == seller_profile or artifact.sold:
        return render(request, "marketplace/simulate_payment.html", {
            'artifact': artifact,
            'error': 'You cannot purchase this item.'
        })

    if request.method == "POST":
        signature = request.POST.get("signature")
        message = request.POST.get("message")

        if not signature or not message:
            return render(request, "marketplace/simulate_payment.html", {
                'artifact': artifact,
                'error': "Missing signature or message."
            })

        # Verify signature using stored public key
        if not verify_signature(buyer_profile.public_key, message, signature):
            return render(request, "marketplace/simulate_payment.html", {
                'artifact': artifact,
                'error': "Invalid digital signature."
            })

        # Wallet logic
        buyer_wallet, _ = Wallet.objects.get_or_create(user_profile=buyer_profile)
        seller_wallet, _ = Wallet.objects.get_or_create(user_profile=seller_profile)
        price = float(artifact.bidding_price)

        if buyer_wallet.get_balance() < price:
            return render(request, "marketplace/simulate_payment.html", {
                'artifact': artifact,
                'error': 'Insufficient funds.',
                'wallet_balance': buyer_wallet.get_balance()
            })

        buyer_wallet.update_balance(-price)
        seller_wallet.update_balance(price)
        artifact.sold = True
        artifact.save()

        PaymentTransaction.objects.create(
            artifact=artifact,
            buyer=buyer_profile,
            seller=seller_profile,
            amount=price,
            status="completed"
        )

        return redirect('marketplace:artifact_list')

    return render(request, "marketplace/simulate_payment.html", {'artifact': artifact})

