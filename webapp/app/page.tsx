import SlugForm from './slug-form';

export default async function Home({
  searchParams,
}: {
  searchParams: { slug?: string }
}) {
  const slug = searchParams.slug;

  if (!slug) {
    return (
      <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
        <h1>タグ選択システム</h1>
        <SlugForm />
        <p>使用方法: 記事のSlugを入力して送信してください</p>
        <p>例: saichan-transition-IMDSv2-netshtrace-20251031</p>
      </div>
    );
  }

  let data: any = null;
  let error: string | null = null;
  let debugInfo: any = {};

  try {
    const lambdaUrl = process.env.LAMBDA_URL || '';
    console.log('[DEBUG] Lambda URL:', lambdaUrl);
    console.log('[DEBUG] Request slug:', slug);
    
    const requestBody = { slug };
    console.log('[DEBUG] Request body:', JSON.stringify(requestBody));
    
    const response = await fetch(lambdaUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
      cache: 'no-store'
    });

    console.log('[DEBUG] Response status:', response.status);
    console.log('[DEBUG] Response headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[DEBUG] Error response:', errorText);
      throw new Error(`Lambda error: ${response.status} - ${errorText}`);
    }

    const responseText = await response.text();
    console.log('[DEBUG] Response body:', responseText);
    
    data = JSON.parse(responseText);
    console.log('[DEBUG] Parsed data:', JSON.stringify(data, null, 2));
    
    debugInfo = {
      lambdaUrl,
      requestSlug: slug,
      responseStatus: response.status,
      responseSize: responseText.length,
      responseData: data
    };
  } catch (e: any) {
    console.error('[DEBUG] Exception:', e);
    error = e.message;
    debugInfo.error = e.stack;
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
        <h1>エラー</h1>
        <p style={{ color: 'red' }}>{error}</p>
      </div>
    );
  }

  const tags = data?.selected_tags || [];
  const cost = data?.cache_info;
  const costJpy = data?.cost_jpy;

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>推奨タグ一覧</h1>
      <SlugForm initialSlug={slug} />
      <p><strong>記事Slug:</strong> {slug}</p>
      
      <table style={{ 
        width: '100%', 
        borderCollapse: 'collapse', 
        marginTop: '1rem',
        border: '1px solid #ddd'
      }}>
        <thead>
          <tr style={{ backgroundColor: '#f5f5f5' }}>
            <th style={{ padding: '0.75rem', border: '1px solid #ddd', textAlign: 'left' }}>タグ名</th>
            <th style={{ padding: '0.75rem', border: '1px solid #ddd', textAlign: 'left' }}>タグID</th>
            <th style={{ padding: '0.75rem', border: '1px solid #ddd', textAlign: 'right' }}>適合度</th>
          </tr>
        </thead>
        <tbody>
          {tags.map((tag: any, idx: number) => (
            <tr key={idx}>
              <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{tag.name}</td>
              <td style={{ padding: '0.75rem', border: '1px solid #ddd' }}>{tag.id}</td>
              <td style={{ padding: '0.75rem', border: '1px solid #ddd', textAlign: 'right' }}>{tag.score}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {cost && (
        <div style={{ 
          marginTop: '2rem', 
          padding: '1rem', 
          backgroundColor: '#f9f9f9', 
          border: '1px solid #ddd',
          borderRadius: '4px'
        }}>
          <h3>コスト情報</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li>入力トークン: {cost.input_tokens?.toLocaleString()}</li>
            <li>出力トークン: {cost.output_tokens?.toLocaleString()}</li>
            <li>総コスト: {costJpy?.total_cost_jpy} 円</li>
            <li>モデル: {data.model}</li>
          </ul>
        </div>
      )}

      <div style={{ 
        marginTop: '2rem', 
        padding: '1rem', 
        backgroundColor: '#fff3cd', 
        border: '1px solid #ffc107',
        borderRadius: '4px'
      }}>
        <h3>デバッグ情報</h3>
        <pre style={{ 
          fontSize: '0.85rem', 
          overflow: 'auto',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-all'
        }}>
          {JSON.stringify(debugInfo, null, 2)}
        </pre>
      </div>
    </div>
  );
}
